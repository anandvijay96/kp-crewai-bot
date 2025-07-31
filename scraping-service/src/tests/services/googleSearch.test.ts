// Test suite for Google Search Service following TDD approach
import GoogleSearchService from '../../services/googleSearch';
import { ServiceConfig } from '../../types/scraping';

// Mock node-fetch completely
jest.mock('node-fetch', () => {
  return jest.fn();
});

const mockFetch = require('node-fetch') as jest.MockedFunction<any>;

describe('GoogleSearchService', () => {
  let googleSearchService: GoogleSearchService;
  let mockConfig: ServiceConfig;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock configuration
    mockConfig = {
      port: 3001,
      pythonBackendUrl: 'http://localhost:8001',
      browser: {
        headless: true,
        viewport: { width: 1280, height: 720 },
        timeout: 30000,
        retries: 2,
        stealthMode: true,
        extensionsEnabled: true,
      },
      rateLimit: {
        requestsPerSecond: 2,
        requestsPerMinute: 120,
        requestsPerHour: 1000,
        burstLimit: 10,
        cooldownPeriod: 2000,
      },
      searchEngines: {
        google: {
          apiKey: 'test-api-key',
          searchEngineId: 'test-search-engine-id',
          dailyLimit: 100,
        },
        bing: {
          apiKey: 'test-bing-key',
          monthlyLimit: 3000,
        },
        duckduckgo: {
          enabled: true,
          maxConcurrent: 5,
        },
      },
      seoQuake: {
        enabled: true,
        timeout: 10000,
      },
    };

    googleSearchService = new GoogleSearchService(mockConfig);
  });

  describe('Initialization', () => {
    it('should initialize with valid configuration', () => {
      const stats = googleSearchService.getStats();
      expect(stats.isConfigured).toBe(true);
      expect(stats.dailyLimit).toBe(100);
      expect(stats.requestCount).toBe(0);
      expect(stats.remainingRequests).toBe(100);
    });

    it('should handle missing API credentials gracefully', () => {
      const invalidConfig = {
        ...mockConfig,
        searchEngines: {
          ...mockConfig.searchEngines,
          google: {
            apiKey: '',
            searchEngineId: '',
            dailyLimit: 100,
          },
        },
      };

      const serviceWithInvalidConfig = new GoogleSearchService(invalidConfig);
      const stats = serviceWithInvalidConfig.getStats();
      expect(stats.isConfigured).toBe(false);
    });
  });

  describe('Search Functionality', () => {
    it('should successfully search and return results', async () => {
      // Mock successful API response
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Test Blog 1',
              link: 'https://example.com/blog1',
              snippet: 'This is a test blog about technology',
            },
            {
              title: 'Test Blog 2',
              link: 'https://example.com/blog2',
              snippet: 'Another test blog about development',
            },
          ],
        })
      });

      const results = await googleSearchService.search('test query', 2);

      expect(results).toHaveLength(2);
      expect(results[0]).toEqual({
        title: 'Test Blog 1',
        url: 'https://example.com/blog1',
        snippet: 'This is a test blog about technology',
        position: 1,
        source: 'google',
      });
      expect(results[1]).toEqual({
        title: 'Test Blog 2',
        url: 'https://example.com/blog2',
        snippet: 'Another test blog about development',
        position: 2,
        source: 'google',
      });
    });

    it('should handle empty search results', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [],
        })
      });

      const results = await googleSearchService.search('no results query');
      expect(results).toHaveLength(0);
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({
          error: { message: 'Daily quota exceeded' }
        })
      });

      await expect(googleSearchService.search('test query')).rejects.toThrow(
        'Google Search API error: 403 - Daily quota exceeded'
      );
    });

    it('should throw error when API credentials are not configured', async () => {
      const invalidConfig = {
        ...mockConfig,
        searchEngines: {
          ...mockConfig.searchEngines,
          google: {
            apiKey: '',
            searchEngineId: '',
            dailyLimit: 100,
          },
        },
      };

      const serviceWithInvalidConfig = new GoogleSearchService(invalidConfig);

      await expect(serviceWithInvalidConfig.search('test query')).rejects.toThrow(
        'Google Search API credentials not configured'
      );
    });

    it('should respect daily request limits', async () => {
      // Set up service with low daily limit
      const limitedConfig = {
        ...mockConfig,
        searchEngines: {
          ...mockConfig.searchEngines,
          google: {
            ...mockConfig.searchEngines.google,
            dailyLimit: 1,
          },
        },
      };

      const limitedService = new GoogleSearchService(limitedConfig);

      // Mock successful response
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Test Blog',
              link: 'https://example.com/blog',
              snippet: 'Test snippet',
            },
          ],
        })
      });

      // First request should succeed
      await limitedService.search('first query');

      // Second request should fail due to daily limit
      await expect(limitedService.search('second query')).rejects.toThrow(
        'Daily limit of 1 searches exceeded'
      );
    });

    it('should limit results to maximum of 10 per request', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: Array.from({ length: 15 }, (_, i) => ({
            title: `Blog ${i + 1}`,
            link: `https://example.com/blog${i + 1}`,
            snippet: `Snippet ${i + 1}`,
          })),
        })
      });

      await googleSearchService.search('test query', 15);

      // Check that the API was called with num=10 (Google's limit)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('&num=10'),
        expect.any(Object)
      );
    });
  });

  describe('Statistics and Management', () => {
    it('should track request count correctly', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Test Blog',
              link: 'https://example.com/blog',
              snippet: 'Test snippet',
            },
          ],
        })
      });

      // Initial stats
      let stats = googleSearchService.getStats();
      expect(stats.requestCount).toBe(0);
      expect(stats.remainingRequests).toBe(100);

      // After one request
      await googleSearchService.search('test query');
      stats = googleSearchService.getStats();
      expect(stats.requestCount).toBe(1);
      expect(stats.remainingRequests).toBe(99);
    });

    it('should reset daily counter', () => {
      // Simulate some requests (we'll directly modify the internal counter for testing)
      googleSearchService.resetDailyCounter();
      
      const stats = googleSearchService.getStats();
      expect(stats.requestCount).toBe(0);
      expect(stats.remainingRequests).toBe(100);
    });
  });

  describe('Edge Cases', () => {
    it('should handle malformed API responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          // Missing items array
          searchInformation: {
            totalResults: '0',
          },
        })
      });

      const results = await googleSearchService.search('test query');
      expect(results).toHaveLength(0);
    });

    it('should filter out results without URLs', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Valid Blog',
              link: 'https://example.com/blog',
              snippet: 'Valid snippet',
            },
            {
              title: 'Invalid Blog',
              // Missing link
              snippet: 'Invalid snippet',
            },
            {
              title: 'Another Valid Blog',
              link: 'https://example.com/blog2',
              snippet: 'Another valid snippet',
            },
          ],
        })
      });

      const results = await googleSearchService.search('test query');
      expect(results).toHaveLength(2); // Should filter out the one without URL
      expect(results.every(result => result.url)).toBe(true);
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(googleSearchService.search('test query')).rejects.toThrow('Network error');
    });

    it('should handle timeout errors', async () => {
      const abortError = new Error('The operation was aborted');
      abortError.name = 'AbortError';
      mockFetch.mockRejectedValue(abortError);

      await expect(googleSearchService.search('test query')).rejects.toThrow(
        'Search request timed out after 5 seconds'
      );
    });
  });

  describe('Performance Optimizations', () => {
    it('should cache search results', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Cached Blog',
              link: 'https://example.com/cached',
              snippet: 'Cached snippet',
            },
          ],
        })
      });

      // First search - should hit API
      const results1 = await googleSearchService.search('cached query');
      expect(results1).toHaveLength(1);
      expect(mockFetch).toHaveBeenCalledTimes(1);

      // Second search with same query - should use cache
      const results2 = await googleSearchService.search('cached query');
      expect(results2).toHaveLength(1);
      expect(mockFetch).toHaveBeenCalledTimes(1); // No additional API call

      // Results should be identical
      expect(results1).toEqual(results2);
    });

    it('should track performance metrics', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              title: 'Test Blog',
              link: 'https://example.com/test',
              snippet: 'Test snippet',
            },
          ],
        })
      });

      // Initial stats
      let stats = googleSearchService.getStats();
      expect(stats.performance.totalRequests).toBe(0);
      expect(stats.performance.cacheHits).toBe(0);
      expect(stats.performance.cacheHitRate).toBe(0);

      // First search
      await googleSearchService.search('perf test');
      stats = googleSearchService.getStats();
      expect(stats.performance.totalRequests).toBe(1);
      expect(stats.performance.averageResponseTime).toBeGreaterThan(0);

      // Second search (cache hit)
      await googleSearchService.search('perf test');
      stats = googleSearchService.getStats();
      expect(stats.performance.totalRequests).toBe(2);
      expect(stats.performance.cacheHits).toBe(1);
      expect(stats.performance.cacheHitRate).toBe(50); // 1 out of 2 requests
    });

    it('should include cache information in stats', () => {
      const stats = googleSearchService.getStats();
      expect(stats.performance).toBeDefined();
      expect(stats.performance.cacheSize).toBeDefined();
      expect(stats.performance.cacheTimeout).toBe(300); // 5 minutes in seconds
    });
  });
});
