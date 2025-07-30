import { ScrapingOptions } from '../src/types/scraping';

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

jest.mock('../src/services/authorityScorer', () => ({
  authorityScorer: {
    getAuthorityScore: jest.fn(() => Promise.resolve({
      domainAuthority: 65,
      pageAuthority: 45,
      source: 'seoguake',
      confidence: 0.85,
      lastUpdated: new Date(),
      metrics: {
        backlinks: 250,
        referringDomains: 100,
        organicTraffic: 5000,
      },
    })),
  },
}));

// Import the WebScraper after mocks are set up
import { WebScraper } from '../src/services/scraper';

const scraper = new WebScraper();

describe('WebScraper Service', () => {
  let mockPage: any;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockPage = {
      setContent: jest.fn(),
      waitForSelector: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn(),
    };

    mockBrowserManager.createPage.mockResolvedValue(mockPage);
    mockBrowserManager.navigateWithRetry.mockResolvedValue(true);
    mockBrowserManager.closePage.mockResolvedValue(undefined);
    mockBrowserManager.getStats.mockReturnValue({
      activePagesCount: 1,
      totalPagesCreated: 10,
      totalPagesClosed: 9,
    });
  });

  describe('scrapeUrl', () => {
    it('should scrape article content correctly', async () => {
      // Mock content type detection
      mockPage.evaluate
        .mockResolvedValueOnce('article') // detectContentType
        .mockResolvedValueOnce('Test Article Title This is the main content of the test article. It contains valuable information about testing web scraping functionality. Another paragraph with more content to test content extraction.') // extractContent
        .mockResolvedValueOnce({ // extractMetadata
          title: 'Test Article Title',
          description: 'Test article description',
          'og:title': 'Test Article Title',
          wordCount: 25,
          linkCount: 2,
          imageCount: 0,
          headingCount: 1,
        })
        .mockResolvedValueOnce([ // extractLinks
          { url: '/home', text: 'Home', type: 'internal' },
          { url: 'https://external.com', text: 'External Link', type: 'external' },
        ]);

      const result = await scraper.scrapeUrl(testUrls.article);
      
      expect(result.success).toBe(true);
      expect(result.contentType).toBe('article');
      expect(result.title).toBe('Test Article Title');
      expect(result.content).toContain('Test Article Title');
      expect(result.content).toContain('main content of the test article');
      expect(result.links).toHaveLength(2);
      expect(result.metadata.wordCount).toBe(25);
      expect(result.responseTime).toBeGreaterThan(0);
    });

    it('should scrape blog content correctly', async () => {
      mockPage.evaluate
        .mockResolvedValueOnce('blog')
        .mockResolvedValueOnce('Blog Post Title This is a blog post content with multiple paragraphs. It should be extracted properly by the scraper.')
        .mockResolvedValueOnce({
          title: 'Blog Post Title',
          description: 'Blog post description',
          wordCount: 18,
          linkCount: 0,
          imageCount: 0,
          headingCount: 1,
        })
        .mockResolvedValueOnce([]);  // no links

      const result = await scraper.scrapeUrl(testUrls.blog);
      
      expect(result.success).toBe(true);
      expect(result.contentType).toBe('blog');
      expect(result.title).toBe('Blog Post Title');
      expect(result.content).toContain('blog post content');
    });

    it('should scrape product page correctly', async () => {
      mockPage.evaluate
        .mockResolvedValueOnce('product')
        .mockResolvedValueOnce('Test Product This is a detailed product description. It includes features and benefits.')
        .mockResolvedValueOnce({
          title: 'Product Name - Store',
          wordCount: 12,
          linkCount: 0,
          imageCount: 1,
          headingCount: 1,
        })
        .mockResolvedValueOnce([]);

      const result = await scraper.scrapeUrl(testUrls.product);
      
      expect(result.success).toBe(true);
      expect(result.contentType).toBe('product');
      expect(result.content).toContain('Test Product');
      expect(result.content).toContain('detailed product description');
    });

    it('should handle scraping with custom options', async () => {
      const options: ScrapingOptions = {
        includeMetadata: true,
        includeImages: true,
        includeLinks: true,
        includeAuthorityScore: true,
        maxContentLength: 100,
        timeout: 15000,
      };

      mockPage.evaluate
        .mockResolvedValueOnce('article')
        .mockResolvedValueOnce('This is a long content that should be truncated because it exceeds the maxContentLength limit set in the options')
        .mockResolvedValueOnce({ title: 'Test Title' })
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce([ // extractImages
          { url: '/image1.jpg', alt: 'Test Image', caption: 'Test Caption' },
        ]);

      const result = await scraper.scrapeUrl(testUrls.article, options);
      
      expect(result.success).toBe(true);
      expect(result.content.length).toBeLessThanOrEqual(100);
      expect(result.images).toHaveLength(1);
      expect(result.authorityScore).toBeDefined();
      expect(result.authorityScore?.domainAuthority).toBe(65);
    });

    it('should handle navigation failure', async () => {
      mockBrowserManager.navigateWithRetry.mockResolvedValueOnce(false);

      const result = await scraper.scrapeUrl(testUrls.invalid);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to navigate');
      expect(result.content).toBe('');
      expect(result.title).toBe('');
    });

    it('should handle page evaluation errors gracefully', async () => {
      mockPage.evaluate.mockRejectedValue(new Error('Page evaluation failed'));

      const result = await scraper.scrapeUrl(testUrls.simple);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Page evaluation failed');
    });

    it('should ensure page is always closed', async () => {
      mockPage.evaluate.mockRejectedValue(new Error('Test error'));

      await scraper.scrapeUrl(testUrls.simple);
      
      expect(mockBrowserManager.closePage).toHaveBeenCalledWith(mockPage);
    });
  });

  describe('batchScrape', () => {
    it('should scrape multiple URLs successfully', async () => {
      const urls = [testUrls.article, testUrls.blog];
      
      mockPage.evaluate
        .mockResolvedValueOnce('article')
        .mockResolvedValueOnce('Article content')
        .mockResolvedValueOnce({ title: 'Article Title' })
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce('blog')
        .mockResolvedValueOnce('Blog content')
        .mockResolvedValueOnce({ title: 'Blog Title' })
        .mockResolvedValueOnce([]);

      const results = await scraper.batchScrape(urls, { concurrentLimit: 2 });
      
      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(true);
      expect(results[0].contentType).toBe('article');
      expect(results[1].contentType).toBe('blog');
    });

    it('should handle partial failures in batch scraping', async () => {
      const urls = [testUrls.article, testUrls.invalid];
      
      mockPage.evaluate
        .mockResolvedValueOnce('article')
        .mockResolvedValueOnce('Article content')
        .mockResolvedValueOnce({ title: 'Article Title' })
        .mockResolvedValueOnce([]);
      
      mockBrowserManager.navigateWithRetry
        .mockResolvedValueOnce(true)  // First URL succeeds
        .mockResolvedValueOnce(false); // Second URL fails

      const results = await scraper.batchScrape(urls);
      
      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(false);
    });
  });

  describe('getStats', () => {
    it('should return browser stats', () => {
      const stats = scraper.getStats();
      
      expect(stats.browserStats).toBeDefined();
      expect(stats.timestamp).toBeInstanceOf(Date);
      expect(mockBrowserManager.getStats).toHaveBeenCalled();
    });
  });
});

