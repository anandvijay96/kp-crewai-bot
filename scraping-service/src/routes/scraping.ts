// API routes for web scraping services
import { Router, Request, Response } from 'express';
import { webScraper } from '../services/scraper';
import { authorityScorer } from '../services/authorityScorer';
import { ScrapingOptions } from '../types/scraping';
import GoogleSearchService from '../services/googleSearch';
import { getConfig } from '../config/config';

const googleSearchService = new GoogleSearchService(getConfig());

const router = Router();

// Validation helper
const validateUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

const validateUrls = (urls: string[]): { valid: boolean; invalidUrls: string[] } => {
  const invalidUrls = urls.filter(url => !validateUrl(url));
  return {
    valid: invalidUrls.length === 0,
    invalidUrls
  };
};

// Error response helper
const errorResponse = (res: Response, status: number, message: string, details?: any) => {
  return res.status(status).json({
    success: false,
    error: message,
    details,
    timestamp: new Date().toISOString()
  });
};

// Success response helper
const successResponse = (res: Response, data: any, message?: string) => {
  return res.json({
    success: true,
    data,
    message,
    timestamp: new Date().toISOString()
  });
};

/**
 * POST /api/scraping/scrape
 * Scrape a single URL
 */
router.post('/scrape', async (req: Request, res: Response) => {
  try {
    const { url, options = {} } = req.body;

    // Validation
    if (!url) {
      return errorResponse(res, 400, 'URL is required');
    }

    if (!validateUrl(url)) {
      return errorResponse(res, 400, 'Invalid URL format');
    }

    // Validate options
    const scrapingOptions: ScrapingOptions = {
      includeMetadata: options.includeMetadata ?? true,
      includeImages: options.includeImages ?? false,
      includeLinks: options.includeLinks ?? true,
      includeAuthorityScore: options.includeAuthorityScore ?? false,
      maxContentLength: Math.min(options.maxContentLength ?? 50000, 100000), // Cap at 100k
      timeout: Math.min(options.timeout ?? 30000, 60000), // Cap at 60s
    };

    console.log(`📡 API: Scraping request for ${url}`);
    const result = await webScraper.scrapeUrl(url, scrapingOptions);

    if (result.success) {
      return successResponse(res, result, 'URL scraped successfully');
    } else {
      return errorResponse(res, 422, 'Failed to scrape URL', { 
        url, 
        error: result.error 
      });
    }

  } catch (error) {
    console.error('API: Error in /scrape:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/scraping/batch-scrape
 * Scrape multiple URLs
 */
router.post('/batch-scrape', async (req: Request, res: Response) => {
  try {
    const { urls, options = {} } = req.body;

    // Validation
    if (!urls || !Array.isArray(urls)) {
      return errorResponse(res, 400, 'URLs array is required');
    }

    if (urls.length === 0) {
      return errorResponse(res, 400, 'At least one URL is required');
    }

    if (urls.length > 50) {
      return errorResponse(res, 400, 'Maximum 50 URLs allowed per batch');
    }

    const urlValidation = validateUrls(urls);
    if (!urlValidation.valid) {
      return errorResponse(res, 400, 'Invalid URL(s) found', {
        invalidUrls: urlValidation.invalidUrls
      });
    }

    // Validate options
    const scrapingOptions: ScrapingOptions = {
      includeMetadata: options.includeMetadata ?? true,
      includeImages: options.includeImages ?? false,
      includeLinks: options.includeLinks ?? true,
      includeAuthorityScore: options.includeAuthorityScore ?? false,
      maxContentLength: Math.min(options.maxContentLength ?? 50000, 100000),
      timeout: Math.min(options.timeout ?? 30000, 60000),
      concurrentLimit: Math.min(options.concurrentLimit ?? 3, 5), // Cap at 5 concurrent
      batchDelay: Math.max(options.batchDelay ?? 2000, 1000), // Min 1s delay
    };

    console.log(`📡 API: Batch scraping request for ${urls.length} URLs`);
    const results = await webScraper.batchScrape(urls, scrapingOptions);

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.length - successCount;

    return successResponse(res, {
      results,
      summary: {
        total: results.length,
        successful: successCount,
        failed: failureCount,
        successRate: `${Math.round((successCount / results.length) * 100)}%`
      }
    }, `Batch scraping completed: ${successCount}/${results.length} successful`);

  } catch (error) {
    console.error('API: Error in /batch-scrape:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/scraping/authority-score
 * Get authority score for a single URL
 */
router.post('/authority-score', async (req: Request, res: Response) => {
  try {
    const { url } = req.body;

    // Validation
    if (!url) {
      return errorResponse(res, 400, 'URL is required');
    }

    if (!validateUrl(url)) {
      return errorResponse(res, 400, 'Invalid URL format');
    }

    console.log(`📡 API: Authority score request for ${url}`);
    const result = await authorityScorer.getAuthorityScore(url);

    return successResponse(res, result, 'Authority score retrieved successfully');

  } catch (error) {
    console.error('API: Error in /authority-score:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/scraping/batch-authority-score
 * Get authority scores for multiple URLs
 */
router.post('/batch-authority-score', async (req: Request, res: Response) => {
  try {
    const { urls } = req.body;

    // Validation
    if (!urls || !Array.isArray(urls)) {
      return errorResponse(res, 400, 'URLs array is required');
    }

    if (urls.length === 0) {
      return errorResponse(res, 400, 'At least one URL is required');
    }

    if (urls.length > 20) {
      return errorResponse(res, 400, 'Maximum 20 URLs allowed per batch for authority scoring');
    }

    const urlValidation = validateUrls(urls);
    if (!urlValidation.valid) {
      return errorResponse(res, 400, 'Invalid URL(s) found', {
        invalidUrls: urlValidation.invalidUrls
      });
    }

    console.log(`📡 API: Batch authority score request for ${urls.length} URLs`);
    const results = await authorityScorer.batchGetAuthorityScores(urls);

    return successResponse(res, {
      results,
      summary: {
        total: results.length,
        averageDomainAuthority: Math.round(
          results.reduce((sum, r) => sum + r.domainAuthority, 0) / results.length
        ),
        averagePageAuthority: Math.round(
          results.reduce((sum, r) => sum + r.pageAuthority, 0) / results.length
        ),
        highConfidenceResults: results.filter(r => r.confidence > 0.7).length
      }
    }, `Authority scores retrieved for ${results.length} URLs`);

  } catch (error) {
    console.error('API: Error in /batch-authority-score:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/scraping/full-analysis
 * Perform comprehensive analysis (scraping + authority scoring)
 */
router.post('/full-analysis', async (req: Request, res: Response) => {
  try {
    const { url, options = {} } = req.body;

    // Validation
    if (!url) {
      return errorResponse(res, 400, 'URL is required');
    }

    if (!validateUrl(url)) {
      return errorResponse(res, 400, 'Invalid URL format');
    }

    // Force include authority score for full analysis
    const scrapingOptions: ScrapingOptions = {
      includeMetadata: options.includeMetadata ?? true,
      includeImages: options.includeImages ?? true,
      includeLinks: options.includeLinks ?? true,
      includeAuthorityScore: true, // Always include for full analysis
      maxContentLength: Math.min(options.maxContentLength ?? 50000, 100000),
      timeout: Math.min(options.timeout ?? 45000, 90000), // Longer timeout for full analysis
    };

    console.log(`📡 API: Full analysis request for ${url}`);
    const scrapingResult = await webScraper.scrapeUrl(url, scrapingOptions);

    if (!scrapingResult.success) {
      return errorResponse(res, 422, 'Failed to analyze URL', { 
        url, 
        error: scrapingResult.error 
      });
    }

    // Calculate additional insights
    const insights = {
      contentQuality: {
        wordCount: scrapingResult.metadata.wordCount || 0,
        readingTime: Math.ceil((scrapingResult.metadata.wordCount || 0) / 200), // minutes
        headingStructure: scrapingResult.metadata.headingCount || 0,
        linkDensity: scrapingResult.links.length / Math.max(scrapingResult.content.length / 100, 1),
      },
      seoMetrics: {
        hasTitle: !!scrapingResult.title,
        hasDescription: !!scrapingResult.metadata.description,
        hasOpenGraph: !!(scrapingResult.metadata['og:title'] || scrapingResult.metadata['og:description']),
        hasStructuredData: !!(scrapingResult.metadata.structuredData && scrapingResult.metadata.structuredData.length > 0),
      },
      authorityMetrics: scrapingResult.authorityScore ? {
        domainAuthority: scrapingResult.authorityScore.domainAuthority,
        pageAuthority: scrapingResult.authorityScore.pageAuthority,
        confidence: scrapingResult.authorityScore.confidence,
        backlinks: scrapingResult.authorityScore.metrics.backlinks,
      } : null
    };

    return successResponse(res, {
      ...scrapingResult,
      insights
    }, 'Full analysis completed successfully');

  } catch (error) {
    console.error('API: Error in /full-analysis:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/scraping/stats
 * Get service statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const scraperStats = webScraper.getStats();
    const authorityStats = authorityScorer.getStats();

    return successResponse(res, {
      scraper: scraperStats,
      authorityScorer: authorityStats,
      service: {
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        platform: process.platform,
        nodeVersion: process.version
      }
    }, 'Service statistics retrieved');

  } catch (error) {
    console.error('API: Error in /stats:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/scraping/blog-discovery
 * Discover blogs using Google Search
 */
router.post('/blog-discovery', async (req: Request, res: Response) => {
  try {
    const { query, numResults } = req.body;

    if (!query) {
      return errorResponse(res, 400, 'Query is required');
    }

    console.log(`📡 API: Blog discovery request with query ${query}`);
    const results = await googleSearchService.search(query, numResults || 10);

    return successResponse(res, results, 'Blog discovery completed successfully');
  } catch (error) {
    console.error('API: Error in /blog-discovery:', error);
    return errorResponse(res, 500, 'Internal server error', {
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
