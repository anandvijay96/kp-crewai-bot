import request from 'supertest';
import express from 'express';
import cors from 'cors';

// Mock the service modules first
jest.mock('../../services/scraper', () => ({
  webScraper: {
    scrapeUrl: jest.fn().mockResolvedValue({
      url: 'https://example.com',
      title: 'Test Page',
      content: 'Test content',
      contentType: 'webpage',
      metadata: {},
      links: [],
      images: [],
      scrapedAt: new Date(),
      responseTime: 1000,
      success: true,
    }),
    batchScrape: jest.fn().mockResolvedValue([]),
    getStats: jest.fn().mockReturnValue({ timestamp: new Date() })
  }
}));

jest.mock('../../services/authorityScorer', () => ({
  authorityScorer: {
    getAuthorityScore: jest.fn().mockResolvedValue({
      domainAuthority: 50,
      pageAuthority: 40,
      source: 'test',
      confidence: 0.8,
      lastUpdated: new Date(),
      metrics: { backlinks: 100, referringDomains: 50, organicTraffic: 1000 }
    }),
    batchGetAuthorityScores: jest.fn().mockResolvedValue([]),
    getStats: jest.fn().mockReturnValue({ timestamp: new Date() })
  }
}));

// Import the main components we want to test integration of
import scrapingRoutes from '../../routes/scraping';
import { generalRateLimit, requestLogger, requestSizeLimit } from '../../middleware/rateLimiter';

describe('API Integration Tests', () => {
  let app: express.Application;

  beforeAll(() => {
    // Set up the app exactly like in main.ts but without WebSocket and browser initialization
    app = express();
    
    // Trust proxy for rate limiting
    app.set('trust proxy', 1);

    // Middleware (same as main.ts)
    app.use(cors({
      origin: ['http://localhost:3000', 'http://localhost:8000'],
      credentials: true
    }));
    app.use(requestLogger);
    app.use(requestSizeLimit(50)); // 50KB request size limit
    app.use(express.json({ limit: '50kb' }));
    app.use(express.urlencoded({ extended: true, limit: '50kb' }));

    // Apply rate limiting
    app.use(generalRateLimit.middleware());

    // API Routes
    app.use('/api/scraping', scrapingRoutes);

    // Health Check Route
    app.get('/health', async (_, res) => {
      res.status(200).json({ status: 'healthy' });
    });
  });

  describe('Health Check Endpoint', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/health');
      
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
    });
  });

  describe('CORS Configuration', () => {
    it('should include CORS headers for allowed origins', async () => {
      const response = await request(app)
        .get('/health')
        .set('Origin', 'http://localhost:3000');

      expect(response.headers['access-control-allow-origin']).toBe('http://localhost:3000');
      expect(response.headers['access-control-allow-credentials']).toBe('true');
    });

    it('should reject requests from disallowed origins', async () => {
      const response = await request(app)
        .get('/health')
        .set('Origin', 'http://malicious-site.com');

      expect(response.headers['access-control-allow-origin']).toBeUndefined();
    });
  });

  describe('Request Logging and ID Generation', () => {
    it('should add request ID to all requests', async () => {
      const response = await request(app).get('/health');
      
      // The requestLogger middleware should add an X-Request-ID header
      expect(response.headers['x-request-id']).toBeDefined();
      expect(typeof response.headers['x-request-id']).toBe('string');
    });
  });

  describe('Rate Limiting Integration', () => {
    it('should include rate limit headers on API requests', async () => {
      const response = await request(app).get('/health');
      
      expect(response.headers['x-ratelimit-limit']).toBeDefined();
      expect(response.headers['x-ratelimit-remaining']).toBeDefined();
      expect(response.headers['x-ratelimit-reset']).toBeDefined();
    });
  });

  describe('Request Size Limiting', () => {
    it('should reject oversized requests', async () => {
      // Create a payload larger than 50KB
      const oversizedPayload = {
        data: 'x'.repeat(60 * 1024) // 60KB
      };

      const response = await request(app)
        .post('/api/scraping/scrape')
        .send(oversizedPayload);

      expect(response.status).toBe(413); // Payload Too Large
    });

    it('should accept requests within size limit', async () => {
      const normalPayload = {
        url: 'https://example.com',
        includeMetadata: true
      };

      const response = await request(app)
        .post('/api/scraping/scrape')
        .send(normalPayload);

      // Should not be rejected for size (might be rejected for other validation reasons)
      expect(response.status).not.toBe(413);
    });
  });

  describe('API Route Integration', () => {
    it('should route scraping requests correctly', async () => {
      const response = await request(app)
        .post('/api/scraping/scrape')
        .send({ url: 'https://example.com' });

      // Should reach the route handler (not 404)
      expect(response.status).not.toBe(404);
    });

    it('should return 404 for non-existent endpoints', async () => {
      const response = await request(app)
        .get('/api/non-existent-endpoint');

      expect(response.status).toBe(404);
    });
  });

  describe('Content-Type Handling', () => {
    it('should parse JSON requests correctly', async () => {
      const payload = { url: 'https://example.com', includeMetadata: true };

      const response = await request(app)
        .post('/api/scraping/scrape')
        .send(payload)
        .set('Content-Type', 'application/json');

      // Should not fail due to JSON parsing
      expect(response.status).not.toBe(400);
    });

    it('should handle malformed JSON gracefully', async () => {
      const response = await request(app)
        .post('/api/scraping/scrape')
        .send('{ invalid json')
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(400);
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle middleware errors gracefully', async () => {
      // This tests the overall error handling of the Express app
      const response = await request(app)
        .post('/api/scraping/scrape')
        .send({}); // Invalid request should trigger validation error

      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('success', false);
      expect(response.body).toHaveProperty('error');
      expect(response.body).toHaveProperty('timestamp');
    });
  });

  describe('API Response Format Consistency', () => {
    it('should return consistent error format across endpoints', async () => {
      const endpoints = [
        '/api/scraping/scrape',
        '/api/scraping/batch-scrape',
        '/api/scraping/authority-score',
        '/api/scraping/batch-authority-score',
        '/api/scraping/full-analysis'
      ];

      for (const endpoint of endpoints) {
        const response = await request(app)
          .post(endpoint)
          .send({}); // Invalid empty request

        expect(response.body).toHaveProperty('success', false);
        expect(response.body).toHaveProperty('error');
        expect(response.body).toHaveProperty('timestamp');
        expect(typeof response.body.timestamp).toBe('string');
      }
    });

    it('should return stats in correct format', async () => {
      const response = await request(app)
        .get('/api/scraping/stats');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('timestamp');
      
      // Since services are mocked, we expect at least the service info to be present
      expect(response.body.data).toHaveProperty('service');
      expect(response.body.data.service).toHaveProperty('uptime');
      expect(response.body.data.service).toHaveProperty('memoryUsage');
      expect(response.body.data.service).toHaveProperty('platform');
      expect(response.body.data.service).toHaveProperty('nodeVersion');
    });
  });
});
