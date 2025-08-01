import fetch from 'node-fetch';
import { SearchEngineResult, ServiceConfig } from '../types/scraping';

class GoogleSearchService {
  private apiKey: string;
  private searchEngineId: string;
  private apiUrl: string = 'https://www.googleapis.com/customsearch/v1';
  private dailyLimit: number;
  private requestCount: number = 0;
  private cache: Map<string, { results: SearchEngineResult[]; timestamp: number }> = new Map();
  private cacheTimeout: number = 5 * 60 * 1000; // 5 minutes cache
  private performanceMetrics: {
    totalRequests: number;
    totalResponseTime: number;
    averageResponseTime: number;
    cacheHits: number;
    cacheHitRate: number;
  } = {
    totalRequests: 0,
    totalResponseTime: 0,
    averageResponseTime: 0,
    cacheHits: 0,
    cacheHitRate: 0
  };

  constructor(config: ServiceConfig) {
    const googleConfig = config.searchEngines.google;
    // Prioritize explicitly passed config over environment variables for testability
    this.apiKey = (googleConfig.apiKey !== undefined) ? googleConfig.apiKey : (process.env.GOOGLE_SEARCH_API_KEY || '');
    this.searchEngineId = (googleConfig.searchEngineId !== undefined) ? googleConfig.searchEngineId : (process.env.GOOGLE_SEARCH_CSE_ID || '');
    this.dailyLimit = googleConfig.dailyLimit || 100;
    
    // Validate configuration
    if (!this.apiKey || !this.searchEngineId) {
      console.warn('⚠️ Google Search API credentials not configured properly');
    }
  }

  async search(query: string, numResults: number = 10): Promise<SearchEngineResult[]> {
    const startTime = Date.now();
    const cacheKey = `${query}-${numResults}`;
    this.performanceMetrics.totalRequests++;

    // Check cache first for performance optimization
    const cachedResult = this.cache.get(cacheKey);
    if (cachedResult && (Date.now() - cachedResult.timestamp) < this.cacheTimeout) {
      this.performanceMetrics.cacheHits++;
      this.updatePerformanceMetrics(Date.now() - startTime);
      console.log(`⚡ Cache hit for query: "${query}" (${cachedResult.results.length} results)`);
      return cachedResult.results;
    }

    // Check if we have valid configuration
    if (!this.apiKey || !this.searchEngineId) {
      throw new Error('Google Search API credentials not configured');
    }

    // Check daily limit
    if (this.requestCount >= this.dailyLimit) {
      throw new Error(`Daily limit of ${this.dailyLimit} searches exceeded`);
    }

    // Ensure we don't exceed Google's limit of 10 results per request
    const limitedResults = Math.min(numResults, 10);
    
    const url = `${this.apiUrl}?key=${this.apiKey}&cx=${this.searchEngineId}&q=${encodeURIComponent(query)}&num=${limitedResults}`;
    
    try {
      console.log(`🔍 Google Search: "${query}" (${limitedResults} results)`);
      
      // Set timeout for faster response
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout
      
      const response = await fetch(url, { 
        signal: controller.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; SEO-Bot/1.0)'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown API error' }));
        const errorMessage = (errorData as any)?.error?.message || 'API request failed';
        throw new Error(`Google Search API error: ${response.status} - ${errorMessage}`);
      }
      
      const data = await response.json();
      this.requestCount++;
      
      const results = this.parseResults(data);
      
      // Cache the results for performance
      this.cache.set(cacheKey, {
        results,
        timestamp: Date.now()
      });
      
      // Clean up old cache entries
      this.cleanupCache();
      
      const responseTime = Date.now() - startTime;
      this.updatePerformanceMetrics(responseTime);
      
      console.log(`✅ Google Search: Found ${results.length} results for "${query}" (${responseTime}ms)`);
      
      return results;
    } catch (error) {
      const responseTime = Date.now() - startTime;
      this.updatePerformanceMetrics(responseTime);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Search request timed out after 5 seconds');
      }
      
      console.error('❌ Google Search API error:', error);
      throw error;
    }
  }

  private parseResults(data: any): SearchEngineResult[] {
    if (!data.items || !Array.isArray(data.items)) {
      console.warn('⚠️ No search results found or invalid response format');
      return [];
    }

    return data.items.map((item: any, index: number) => ({
      title: item.title || 'No title',
      url: item.link || '',
      snippet: item.snippet || 'No description available',
      position: index + 1,
      source: 'google' as const,
    })).filter((result: SearchEngineResult) => result.url); // Filter out results without URLs
  }

  // Update performance metrics
  private updatePerformanceMetrics(responseTime: number) {
    this.performanceMetrics.totalResponseTime += responseTime;
    this.performanceMetrics.averageResponseTime = 
      this.performanceMetrics.totalResponseTime / this.performanceMetrics.totalRequests;
    this.performanceMetrics.cacheHitRate = 
      (this.performanceMetrics.cacheHits / this.performanceMetrics.totalRequests) * 100;
  }

  // Clean up old cache entries
  private cleanupCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheTimeout) {
        this.cache.delete(key);
      }
    }
  }

  // Get current usage stats with performance metrics
  getStats() {
    return {
      requestCount: this.requestCount,
      dailyLimit: this.dailyLimit,
      remainingRequests: Math.max(0, this.dailyLimit - this.requestCount),
      isConfigured: !!(this.apiKey && this.searchEngineId),
      performance: {
        ...this.performanceMetrics,
        cacheSize: this.cache.size,
        cacheTimeout: this.cacheTimeout / 1000 // in seconds
      }
    };
  }

  // Reset daily counter (can be called manually or scheduled)
  resetDailyCounter() {
    this.requestCount = 0;
    console.log('🔄 Google Search: Daily counter reset');
  }
}

export default GoogleSearchService;
