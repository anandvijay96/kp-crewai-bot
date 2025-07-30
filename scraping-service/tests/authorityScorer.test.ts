// Mock browser manager
const mockBrowserManager = {
  createPage: jest.fn(),
  navigateWithRetry: jest.fn(),
  injectSEOQuake: jest.fn(),
  closePage: jest.fn(),
  getStats: jest.fn(),
  initialize: jest.fn(),
  isInitialized: jest.fn(),
  close: jest.fn(),
};

// Test URLs
const testUrls = {
  article: 'https://dev.to/test-article',
  blog: 'https://medium.com/test-blog',
  product: 'https://example-store.com/product/123',
  documentation: 'https://docs.example.com/api',
  simple: 'https://example.com',
  invalid: 'https://invalid-url-that-does-not-exist.com',
};

jest.mock('../src/utils/browser', () => ({
  getBrowserManager: () => mockBrowserManager,
}));

// Import the AuthorityScorer after mocks are set up
import { AuthorityScorer } from '../src/services/authorityScorer';

const authorityScorer = new AuthorityScorer();

describe('AuthorityScorer Service', () => {
  let mockPage: any;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockPage = {
      evaluate: jest.fn(),
    };

    mockBrowserManager.createPage.mockResolvedValue(mockPage);
    mockBrowserManager.navigateWithRetry.mockResolvedValue(true);
    mockBrowserManager.injectSEOQuake.mockResolvedValue(undefined);
    mockBrowserManager.closePage.mockResolvedValue(undefined);
    mockBrowserManager.getStats.mockReturnValue({
      activePagesCount: 1,
      totalPagesCreated: 5,
      totalPagesClosed: 4,
    });
  });

  describe('getAuthorityScore', () => {
    it('should get authority score with SEOquake data', async () => {
      // Mock SEOquake data extraction
      mockPage.evaluate
        .mockResolvedValueOnce({ // extractAuthorityMetrics
          domainAuthority: 65,
          pageAuthority: 45,
        })
        .mockResolvedValueOnce({ // getAdditionalMetrics
          backlinks: 250,
          referringDomains: 100,
          organicTraffic: 5000,
        });

      const result = await authorityScorer.getAuthorityScore(testUrls.article);
      
      expect(result.domainAuthority).toBe(65);
      expect(result.pageAuthority).toBe(45);
      expect(result.source).toBe('seoguake');
      expect(result.confidence).toBeGreaterThan(0.5);
      expect(result.metrics.backlinks).toBe(250);
      expect(result.metrics.referringDomains).toBe(100);
      expect(result.metrics.organicTraffic).toBe(5000);
      expect(result.lastUpdated).toBeInstanceOf(Date);
    });

    it('should calculate confidence correctly for high-quality metrics', async () => {
      mockPage.evaluate
        .mockResolvedValueOnce({
          domainAuthority: 80,
          pageAuthority: 70,
        })
        .mockResolvedValueOnce({
          backlinks: 500,
          referringDomains: 150,
          organicTraffic: 10000,
        });

      const result = await authorityScorer.getAuthorityScore(testUrls.article);
      
      // Should have high confidence due to good metrics
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    it('should handle SEOquake unavailable gracefully', async () => {
      // Mock fallback when SEOquake is not available
      mockPage.evaluate
        .mockResolvedValueOnce({
          domainAuthority: 45, // fallback values
          pageAuthority: 35,
        })
        .mockResolvedValueOnce({
          backlinks: 150,
          referringDomains: 75,
          organicTraffic: 2500,
        });

      const result = await authorityScorer.getAuthorityScore(testUrls.simple);
      
      expect(result.domainAuthority).toBeDefined();
      expect(result.pageAuthority).toBeDefined();
      expect(result.source).toBe('seoguake');
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should handle navigation failure with fallback score', async () => {
      mockBrowserManager.navigateWithRetry.mockResolvedValueOnce(false);

      const result = await authorityScorer.getAuthorityScore(testUrls.invalid);
      
      expect(result.source).toBe('fallback');
      expect(result.confidence).toBe(0.3);
      expect(result.domainAuthority).toBeGreaterThanOrEqual(10);
      expect(result.domainAuthority).toBeLessThanOrEqual(100);
      expect(result.pageAuthority).toBeGreaterThanOrEqual(10);
      expect(result.pageAuthority).toBeLessThanOrEqual(100);
    });

    it('should provide higher scores for well-known domains', async () => {
      mockBrowserManager.navigateWithRetry.mockResolvedValueOnce(false);

      const result = await authorityScorer.getAuthorityScore('https://medium.com/article');
      
      expect(result.source).toBe('fallback');
      expect(result.domainAuthority).toBeGreaterThan(50); // Well-known domains get higher base scores
    });

    it('should handle page evaluation errors', async () => {
      mockPage.evaluate.mockRejectedValue(new Error('Page evaluation failed'));

      const result = await authorityScorer.getAuthorityScore(testUrls.simple);
      
      expect(result.source).toBe('fallback');
      expect(result.confidence).toBe(0.3);
    });

    it('should ensure page is always closed', async () => {
      mockPage.evaluate.mockRejectedValue(new Error('Test error'));

      await authorityScorer.getAuthorityScore(testUrls.simple);
      
      expect(mockBrowserManager.closePage).toHaveBeenCalledWith(mockPage);
    });
  });

  describe('batchGetAuthorityScores', () => {
    it('should process multiple URLs successfully', async () => {
      const urls = [testUrls.article, testUrls.blog];
      
      mockPage.evaluate
        // First URL
        .mockResolvedValueOnce({ domainAuthority: 65, pageAuthority: 45 })
        .mockResolvedValueOnce({ backlinks: 250, referringDomains: 100, organicTraffic: 5000 })
        // Second URL
        .mockResolvedValueOnce({ domainAuthority: 55, pageAuthority: 40 })
        .mockResolvedValueOnce({ backlinks: 180, referringDomains: 80, organicTraffic: 3000 });

      const results = await authorityScorer.batchGetAuthorityScores(urls);
      
      expect(results).toHaveLength(2);
      expect(results[0].domainAuthority).toBe(65);
      expect(results[1].domainAuthority).toBe(55);
      expect(results[0].source).toBe('seoguake');
      expect(results[1].source).toBe('seoguake');
    });

    it('should handle partial failures in batch processing', async () => {
      const urls = [testUrls.article, testUrls.invalid];
      
      mockPage.evaluate
        .mockResolvedValueOnce({ domainAuthority: 65, pageAuthority: 45 })
        .mockResolvedValueOnce({ backlinks: 250, referringDomains: 100, organicTraffic: 5000 });
      
      mockBrowserManager.navigateWithRetry
        .mockResolvedValueOnce(true)  // First URL succeeds
        .mockResolvedValueOnce(false); // Second URL fails

      const results = await authorityScorer.batchGetAuthorityScores(urls);
      
      expect(results).toHaveLength(2);
      expect(results[0].source).toBe('seoguake');
      expect(results[1].source).toBe('fallback');
    });

    it('should respect concurrent limit', async () => {
      const urls = Array(5).fill(testUrls.simple);
      
      mockPage.evaluate
        .mockResolvedValue({ domainAuthority: 50, pageAuthority: 35 })
        .mockResolvedValue({ backlinks: 150, referringDomains: 75, organicTraffic: 2500 });

      const startTime = Date.now();
      await authorityScorer.batchGetAuthorityScores(urls);
      const endTime = Date.now();
      
      // Should take some time due to rate limiting
      expect(endTime - startTime).toBeGreaterThan(1000);
    });
  });

  describe('getStats', () => {
    it('should return browser stats', () => {
      const stats = authorityScorer.getStats();
      
      expect(stats.browserStats).toBeDefined();
      expect(stats.timestamp).toBeInstanceOf(Date);
      expect(mockBrowserManager.getStats).toHaveBeenCalled();
    });
  });

  describe('confidence calculation', () => {
    it('should give higher confidence for normal DA/PA relationship', async () => {
      mockPage.evaluate
        .mockResolvedValueOnce({
          domainAuthority: 70,
          pageAuthority: 60, // DA > PA (normal)
        })
        .mockResolvedValueOnce({
          backlinks: 300,
          referringDomains: 120,
          organicTraffic: 8000,
        });

      const result = await authorityScorer.getAuthorityScore(testUrls.article);
      
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    it('should adjust confidence based on supporting metrics', async () => {
      mockPage.evaluate
        .mockResolvedValueOnce({
          domainAuthority: 60,
          pageAuthority: 50,
        })
        .mockResolvedValueOnce({
          backlinks: 50,  // Low backlinks
          referringDomains: 20, // Low referring domains
          organicTraffic: 500, // Low traffic
        });

      const result = await authorityScorer.getAuthorityScore(testUrls.article);
      
      // Should have lower confidence due to poor supporting metrics
      expect(result.confidence).toBeLessThan(0.8);
    });
  });
});
