// Core web scraping service for extracting content from URLs
import { Page } from 'puppeteer';
import { ContentScrapingResult, ScrapingOptions, ContentType } from '../types/scraping';
import { getBrowserManager } from '../utils/browser';
import { authorityScorer } from './authorityScorer';

export class WebScraper {
  private browserManager?: any;
  
  private getBrowserManager() {
    if (!this.browserManager) {
      this.browserManager = getBrowserManager();
    }
    return this.browserManager;
  }

  async scrapeUrl(url: string, options: ScrapingOptions = {}): Promise<ContentScrapingResult> {
    console.log(`🌐 Starting scraping for: ${url}`);
    
    const startTime = Date.now();
    const browserManager = this.getBrowserManager();
    const page = await browserManager.createPage();

    try {
      // Set default options
      const scrapeOptions = {
        includeMetadata: true,
        includeImages: false,
        includeLinks: true,
        maxContentLength: 50000,
        timeout: 30000,
        ...options
      };

      // Navigate to the URL
      const navigationSuccess = await browserManager.navigateWithRetry(page, url);
      
      if (!navigationSuccess) {
        throw new Error(`Failed to navigate to ${url}`);
      }

      // Wait for content to load  
      await page.waitForSelector('body', { timeout: scrapeOptions.timeout });
      
      // Extract content based on detected content type
      const contentType = await this.detectContentType(page);
      const content = await this.extractContent(page, contentType, scrapeOptions);
      
      // Extract metadata
      const metadata = scrapeOptions.includeMetadata ? await this.extractMetadata(page) : {};
      
      // Extract links if requested
      const links = scrapeOptions.includeLinks ? await this.extractLinks(page) : [];
      
      // Extract images if requested
      const images = scrapeOptions.includeImages ? await this.extractImages(page) : [];

      // Get authority score if requested
      let authorityScore;
      if (scrapeOptions.includeAuthorityScore) {
        try {
          authorityScore = await authorityScorer.getAuthorityScore(url);
        } catch (error) {
          console.warn('Failed to get authority score:', error);
        }
      }

      const responseTime = Date.now() - startTime;

      const result: ContentScrapingResult = {
        url,
        title: metadata.title || '',
        content: (content || '').substring(0, scrapeOptions.maxContentLength),
        contentType,
        metadata,
        links,
        images,
        authorityScore,
        scrapedAt: new Date(),
        responseTime,
        success: true,
      };

      console.log(`✅ Successfully scraped ${url} in ${responseTime}ms (${content.length} chars)`);
      return result;

    } catch (error) {
      const responseTime = Date.now() - startTime;
      console.error(`❌ Error scraping ${url}:`, error);
      
      return {
        url,
        title: '',
        content: '',
        contentType: 'unknown',
        metadata: {},
        links: [],
        images: [],
        scrapedAt: new Date(),
        responseTime,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    } finally {
      await browserManager.closePage(page);
    }
  }

  private async detectContentType(page: Page): Promise<ContentType> {
    try {
      const contentType = await page.evaluate(() => {
        // Check for article indicators
        const articleSelectors = [
          'article',
          '[role="article"]',
          '.article',
          '.post',
          '.blog-post',
          '.entry-content',
          '.post-content'
        ];

        if (articleSelectors.some(selector => document.querySelector(selector))) {
          return 'article';
        }

        // Check for blog indicators
        const blogSelectors = [
          '.blog',
          '.post-list',
          '.articles',
          '[class*="blog"]'
        ];

        if (blogSelectors.some(selector => document.querySelector(selector))) {
          return 'blog';
        }

        // Check for product page indicators
        const productSelectors = [
          '.product',
          '[itemtype*="Product"]',
          '.price',
          '.add-to-cart',
          '.buy-now'
        ];

        if (productSelectors.some(selector => document.querySelector(selector))) {
          return 'product';
        }

        // Check for documentation indicators
        const docSelectors = [
          '.documentation',
          '.docs',
          '.api-docs',
          '.reference'
        ];

        if (docSelectors.some(selector => document.querySelector(selector))) {
          return 'documentation';
        }

        // Default to webpage
        return 'webpage';
      });

      return contentType;
    } catch (error) {
      console.error('Error detecting content type:', error);
      return 'webpage';
    }
  }

  private async extractContent(page: Page, contentType: ContentType, options: ScrapingOptions): Promise<string> {
    try {
      const content = await page.evaluate((type) => {
        // Remove script and style elements
        const scripts = document.querySelectorAll('script, style, noscript');
        scripts.forEach(el => el.remove());

        let mainContent = '';

        // Content extraction strategies based on type
        switch (type) {
          case 'article':
            // Try article-specific selectors first
            const articleSelectors = [
              'article',
              '[role="article"]',
              '.article-content',
              '.post-content',
              '.entry-content',
              '.content',
              'main'
            ];

            for (const selector of articleSelectors) {
              const element = document.querySelector(selector);
              if (element) {
                mainContent = (element as HTMLElement).innerText;
                break;
              }
            }
            break;

          case 'blog':
            const blogSelectors = [
              '.post-content',
              '.blog-content',
              '.entry-content',
              'article',
              'main'
            ];

            for (const selector of blogSelectors) {
              const element = document.querySelector(selector);
              if (element) {
                mainContent = (element as HTMLElement).innerText;
                break;
              }
            }
            break;

          case 'product':
            const productSelectors = [
              '.product-description',
              '.product-details',
              '.description',
              '.product-info'
            ];

            const productParts: string[] = [];
            
            // Get product title
            const titleEl = document.querySelector('h1, .product-title, .title');
            if (titleEl) productParts.push((titleEl as HTMLElement).innerText);

            // Get product description
            for (const selector of productSelectors) {
              const element = document.querySelector(selector);
              if (element) {
                productParts.push((element as HTMLElement).innerText);
                break;
              }
            }

            mainContent = productParts.join('\n\n');
            break;

          default:
            // General content extraction
            const generalSelectors = [
              'main',
              '[role="main"]',
              '.main-content',
              '.content',
              '.container',
              'body'
            ];

            for (const selector of generalSelectors) {
              const element = document.querySelector(selector);
              if (element) {
                mainContent = (element as HTMLElement).innerText;
                break;
              }
            }
        }

        // Fallback to body if no content found
        if (!mainContent.trim()) {
          mainContent = document.body.innerText;
        }

        // Clean up the content
        return mainContent
          .replace(/\s+/g, ' ')
          .replace(/\n\s*\n/g, '\n')
          .trim();

      }, contentType);

      return content;
    } catch (error) {
      console.error('Error extracting content:', error);
      return '';
    }
  }

  private async extractMetadata(page: Page): Promise<Record<string, any>> {
    try {
      const metadata = await page.evaluate(() => {
        const meta: Record<string, any> = {};

        // Basic metadata
        meta.title = document.title;
        meta.url = window.location.href;

        // Meta tags
        const metaTags = document.querySelectorAll('meta');
        metaTags.forEach(tag => {
          const name = tag.getAttribute('name') || tag.getAttribute('property');
          const content = tag.getAttribute('content');
          
          if (name && content) {
            meta[name] = content;
          }
        });

        // Structured data
        const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
        const structuredData: any[] = [];
        
        jsonLdScripts.forEach(script => {
          try {
            const data = JSON.parse(script.textContent || '');
            structuredData.push(data);
          } catch (e) {
            // Invalid JSON, skip
          }
        });

        if (structuredData.length > 0) {
          meta.structuredData = structuredData;
        }

        // Additional metrics
        meta.wordCount = document.body.innerText.split(/\s+/).length;
        meta.linkCount = document.querySelectorAll('a').length;
        meta.imageCount = document.querySelectorAll('img').length;
        meta.headingCount = document.querySelectorAll('h1, h2, h3, h4, h5, h6').length;

        return meta;
      });

      return metadata;
    } catch (error) {
      console.error('Error extracting metadata:', error);
      return {};
    }
  }

  private async extractLinks(page: Page): Promise<Array<{ url: string; text: string; type: string }>> {
    try {
      const links = await page.evaluate(() => {
        const linkElements = document.querySelectorAll('a[href]');
        const links: Array<{ url: string; text: string; type: string }> = [];

        linkElements.forEach(link => {
          const href = link.getAttribute('href');
          const text = link.textContent?.trim() || '';
          
          if (href && text) {
            let type = 'internal';
            
            try {
              const url = new URL(href, window.location.href);
              type = url.hostname === window.location.hostname ? 'internal' : 'external';
            } catch (e) {
              type = 'relative';
            }

            links.push({
              url: href,
              text,
              type
            });
          }
        });

        return links;
      });

      return links;
    } catch (error) {
      console.error('Error extracting links:', error);
      return [];
    }
  }

  private async extractImages(page: Page): Promise<Array<{ url: string; alt: string; caption?: string }>> {
    try {
      const images = await page.evaluate(() => {
        const imgElements = document.querySelectorAll('img[src]');
        const images: Array<{ url: string; alt: string; caption?: string }> = [];

        imgElements.forEach(img => {
          const src = img.getAttribute('src');
          const alt = img.getAttribute('alt') || '';
          
          if (src) {
            const imageData: { url: string; alt: string; caption?: string } = {
              url: src,
              alt
            };

            // Look for captions
            const figure = img.closest('figure');
            if (figure) {
              const caption = figure.querySelector('figcaption');
              if (caption) {
                imageData.caption = caption.textContent?.trim();
              }
            }

            images.push(imageData);
          }
        });

        return images;
      });

      return images;
    } catch (error) {
      console.error('Error extracting images:', error);
      return [];
    }
  }

  async batchScrape(urls: string[], options: ScrapingOptions = {}): Promise<ContentScrapingResult[]> {
    console.log(`🔄 Starting batch scraping for ${urls.length} URLs...`);
    
    const results: ContentScrapingResult[] = [];
    const concurrentLimit = options.concurrentLimit || 3;
    
    for (let i = 0; i < urls.length; i += concurrentLimit) {
      const batch = urls.slice(i, i + concurrentLimit);
      const batchPromises = batch.map(url => this.scrapeUrl(url, options));
      
      try {
        const batchResults = await Promise.allSettled(batchPromises);
        
        batchResults.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            results.push(result.value);
          } else {
            console.error(`Failed to scrape ${batch[index]}:`, result.reason);
            results.push({
              url: batch[index],
              title: '',
              content: '',
              contentType: 'unknown',
              metadata: {},
              links: [],
              images: [],
              scrapedAt: new Date(),
              responseTime: 0,
              success: false,
              error: result.reason?.toString() || 'Unknown error',
            });
          }
        });
        
        // Rate limiting delay between batches
        if (i + concurrentLimit < urls.length) {
          const delay = options.batchDelay || 2000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      } catch (error) {
        console.error('Error in batch processing:', error);
        
        // Add error results for the entire batch
        batch.forEach(url => {
          results.push({
            url,
            title: '',
            content: '',
            contentType: 'unknown',
            metadata: {},
            links: [],
            images: [],
            scrapedAt: new Date(),
            responseTime: 0,
            success: false,
            error: 'Batch processing error',
          });
        });
      }
    }
    
    console.log(`✅ Completed batch scraping: ${results.filter(r => r.success).length}/${results.length} successful`);
    return results;
  }

  getStats() {
    const browserManager = this.getBrowserManager();
    return {
      browserStats: browserManager.getStats(),
      timestamp: new Date(),
    };
  }
}

// Export singleton instance
export const webScraper = new WebScraper();
