// Test suite for Blog Discovery Route following TDD approach
import request from 'supertest';
import express from 'express';
import scrapingRoutes from '../../routes/scraping';

// Mock the GoogleSearchService
jest.mock('../../services/googleSearch');
const MockedGoogleSearchService = require('../../services/googleSearch').default;

describe('Blog Discovery Route', () => {
  let app: express.Application;
  let mockGoogleSearch: jest.Mocked<any>;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    app.use('/api/scraping', scrapingRoutes);

    // Create a mock instance
    mockGoogleSearch = {
      search: jest.fn(),
      getStats: jest.fn(),
      resetDailyCounter: jest.fn(),
    };

    // Mock the constructor to return our mock instance
    MockedGoogleSearchService.mockImplementation(() => mockGoogleSearch);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/scraping/blog-discovery', () => {
    it('should return 400 when query is missing', async () => {
      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Query is required');
    });

    it('should successfully discover blogs with Google Search', async () => {
      const mockSearchResults = [
        {
          title: 'Tech Blog 1',
          url: 'https://techblog1.com',
          snippet: 'A great tech blog about programming',
          position: 1,
          source: 'google',
        },
        {
          title: 'Dev Blog 2',
          url: 'https://devblog2.com',
          snippet: 'Development tutorials and tips',
          position: 2,
          source: 'google',
        },
      ];

      mockGoogleSearch.search.mockResolvedValue(mockSearchResults);

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'tech blog programming',
          numResults: 2,
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Blog discovery completed successfully');
      expect(response.body.data).toEqual(mockSearchResults);
      expect(mockGoogleSearch.search).toHaveBeenCalledWith('tech blog programming', 2);
    });

    it('should use default numResults when not provided', async () => {
      const mockSearchResults = [
        {
          title: 'Blog 1',
          url: 'https://blog1.com',
          snippet: 'Blog snippet',
          position: 1,
          source: 'google',
        },
      ];

      mockGoogleSearch.search.mockResolvedValue(mockSearchResults);

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'test query',
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(mockGoogleSearch.search).toHaveBeenCalledWith('test query', 10);
    });

    it('should handle empty search results', async () => {
      mockGoogleSearch.search.mockResolvedValue([]);

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'no results query',
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toEqual([]);
    });

    it('should handle Google Search API errors', async () => {
      mockGoogleSearch.search.mockRejectedValue(new Error('API quota exceeded'));

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'test query',
        });

      expect(response.status).toBe(500);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Internal server error');
      expect(response.body.details.message).toBe('API quota exceeded');
    });

    it('should handle configuration errors gracefully', async () => {
      mockGoogleSearch.search.mockRejectedValue(new Error('Google Search API credentials not configured'));

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'test query',
        });

      expect(response.status).toBe(500);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Internal server error');
      expect(response.body.details.message).toBe('Google Search API credentials not configured');
    });

    it('should handle various query types', async () => {
      const testCases = [
        'programming blog',
        'tech blog "write for us"',
        'site:medium.com programming',
        'inurl:blog javascript',
      ];

      for (const query of testCases) {
        mockGoogleSearch.search.mockResolvedValue([
          {
            title: 'Test Blog',
            url: 'https://testblog.com',
            snippet: 'Test snippet',
            position: 1,
            source: 'google',
          },
        ]);

        const response = await request(app)
          .post('/api/scraping/blog-discovery')
          .send({ query });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(mockGoogleSearch.search).toHaveBeenCalledWith(query, 10);
      }
    });

    it('should handle special characters in queries', async () => {
      const specialQuery = 'programming & development "best practices"';
      
      mockGoogleSearch.search.mockResolvedValue([]);

      const response = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: specialQuery,
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(mockGoogleSearch.search).toHaveBeenCalledWith(specialQuery, 10);
    });

    it('should validate numResults parameter bounds', async () => {
      mockGoogleSearch.search.mockResolvedValue([]);

      // Test with large numResults
      const response1 = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'test query',
          numResults: 50,
        });

      expect(response1.status).toBe(200);
      expect(mockGoogleSearch.search).toHaveBeenCalledWith('test query', 50);

      // Test with zero numResults
      const response2 = await request(app)
        .post('/api/scraping/blog-discovery')
        .send({
          query: 'test query',
          numResults: 0,
        });

      expect(response2.status).toBe(200);
      expect(mockGoogleSearch.search).toHaveBeenCalledWith('test query', 0);
    });
  });

  describe('Integration with other routes', () => {
    it('should work alongside existing scraping routes', async () => {
      // Test that the new route doesn't interfere with existing functionality
      const response = await request(app)
        .get('/api/scraping/stats');

      // This should still work (stats endpoint)
      expect(response.status).toBe(200);
    });
  });
});
