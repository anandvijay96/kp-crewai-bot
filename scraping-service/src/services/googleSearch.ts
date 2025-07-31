import fetch from 'node-fetch';
import { SearchEngineResult, ServiceConfig } from '../types/scraping';

class GoogleSearchService {
  private apiKey: string;
  private searchEngineId: string;
  private apiUrl: string = 'https://www.googleapis.com/customsearch/v1';
  private dailyLimit: number;
  private requestCount: number = 0;

  constructor(config: ServiceConfig) {
    const googleConfig = config.searchEngines.google;
    this.apiKey = googleConfig.apiKey || process.env.GOOGLE_SEARCH_API_KEY || '';
    this.searchEngineId = googleConfig.searchEngineId || process.env.GOOGLE_SEARCH_CSE_ID || '';
    this.dailyLimit = googleConfig.dailyLimit || 100;
    
    // Validate configuration
    if (!this.apiKey || !this.searchEngineId) {
      console.warn('⚠️ Google Search API credentials not configured properly');
    }
  }

  async search(query: string, numResults: number = 10): Promise<SearchEngineResult[]> {
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
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown API error' }));
        const errorMessage = (errorData as any)?.error?.message || 'API request failed';
        throw new Error(`Google Search API error: ${response.status} - ${errorMessage}`);
      }
      
      const data = await response.json();
      this.requestCount++;
      
      const results = this.parseResults(data);
      console.log(`✅ Google Search: Found ${results.length} results for "${query}"`);
      
      return results;
    } catch (error) {
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

  // Get current usage stats
  getStats() {
    return {
      requestCount: this.requestCount,
      dailyLimit: this.dailyLimit,
      remainingRequests: Math.max(0, this.dailyLimit - this.requestCount),
      isConfigured: !!(this.apiKey && this.searchEngineId),
    };
  }

  // Reset daily counter (can be called manually or scheduled)
  resetDailyCounter() {
    this.requestCount = 0;
    console.log('🔄 Google Search: Daily counter reset');
  }
}

export default GoogleSearchService;
