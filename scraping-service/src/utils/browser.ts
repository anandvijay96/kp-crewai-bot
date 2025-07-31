// Browser utility with Puppeteer and stealth capabilities
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { Browser, Page, LaunchOptions } from 'puppeteer';
import { BrowserConfig } from '../types/scraping';

// Enable stealth mode
puppeteer.use(StealthPlugin());

export class BrowserManager {
  private browser: Browser | null = null;
  private config: BrowserConfig;
  private activePagesCount = 0;
  private startTime = Date.now();

  constructor(config: BrowserConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    if (this.browser) {
      return; // Already initialized
    }

    console.log('🚀 Initializing browser with stealth mode...');
    
    const launchOptions: LaunchOptions = {
      headless: this.config.headless ? 'new' : false, // Use new headless mode
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-blink-features=AutomationControlled',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-background-networking',
        '--disable-extensions-except=./extensions', // Allow our extensions
        '--load-extension=./extensions', // Load SEOquake if available
        '--disable-plugins',
        '--disable-default-apps',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-component-update',
        `--window-size=${this.config.viewport.width},${this.config.viewport.height}`,
      ],
      timeout: this.config.timeout,
      defaultViewport: {
        width: this.config.viewport.width,
        height: this.config.viewport.height,
      },
    };

    // Add proxy configuration if provided
    if (this.config.proxyConfig) {
      launchOptions.args?.push(`--proxy-server=${this.config.proxyConfig.server}`);
    }

    try {
      this.browser = await puppeteer.launch(launchOptions);
      console.log('✅ Browser initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize browser:', error);
      throw error;
    }
  }

  async createPage(): Promise<Page> {
    if (!this.browser) {
      await this.initialize();
    }

    if (!this.browser) {
      throw new Error('Browser initialization failed');
    }

    const page = await this.browser.newPage();
    this.activePagesCount++;

    // Set user agent if provided
    if (this.config.userAgent) {
      await page.setUserAgent(this.config.userAgent);
    }

    // Set viewport
    await page.setViewport(this.config.viewport);

    // Configure proxy authentication if needed
    if (this.config.proxyConfig?.username && this.config.proxyConfig?.password) {
      await page.authenticate({
        username: this.config.proxyConfig.username,
        password: this.config.proxyConfig.password,
      });
    }

    // Add stealth configurations
    await this.configureStealth(page);

    // Add performance monitoring
    this.setupPageMonitoring(page);

    return page;
  }

  private async configureStealth(page: Page): Promise<void> {
    // Override the webdriver property
    await page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });

    // Mock languages and plugins
    await page.evaluateOnNewDocument(() => {
      // Mock languages
      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
      });

      // Mock plugins
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
      });
    });

    // Set realistic headers
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0',
    });
  }

  private setupPageMonitoring(page: Page): void {
    page.on('close', () => {
      this.activePagesCount--;
    });

    page.on('error', (error) => {
      console.error('Page error:', error);
    });

    page.on('pageerror', (error) => {
      console.error('Page script error:', error);
    });
  }

  async closePage(page: Page): Promise<void> {
    try {
      await page.close();
    } catch (error) {
      console.error('Error closing page:', error);
    }
  }

  async navigateWithRetry(page: Page, url: string, maxRetries: number = 3): Promise<boolean> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🌐 Navigating to ${url} (attempt ${attempt}/${maxRetries})`);
        
        // Add random delay to appear more human-like
        const delay = Math.random() * 1000 + 500; // 0.5-1.5 seconds
        await new Promise(resolve => setTimeout(resolve, delay));

        // Block unnecessary resources for faster loading
        await page.setRequestInterception(true);
        page.on('request', (req) => {
          const resourceType = req.resourceType();
          if (resourceType === 'image' || resourceType === 'stylesheet' || resourceType === 'font') {
            req.abort();
          } else {
            req.continue();
          }
        });

        // Try different waitUntil strategies based on attempt
        const waitStrategy = attempt === 1 ? 'domcontentloaded' : 
                           attempt === 2 ? 'networkidle2' : 'load';
        
        const response = await page.goto(url, { 
          waitUntil: waitStrategy as any,
          timeout: Math.min(this.config.timeout, 45000) // Cap at 45s per attempt
        });

        if (response && (response.ok() || response.status() < 400)) {
          console.log(`✅ Navigation successful with status: ${response.status()}`);
          return true;
        } else {
          console.log(`⚠️ Navigation returned status: ${response?.status()}`);
          if (response && response.status() >= 400 && response.status() < 500) {
            // Client error, don't retry
            return false;
          }
        }
      } catch (error) {
        console.error(`❌ Navigation attempt ${attempt} failed:`, error);
        
        // Check if it's a timeout error
        const isTimeout = error instanceof Error && 
          (error.message.includes('timeout') || error.message.includes('Navigation timeout'));
        
        if (attempt < maxRetries) {
          // Use shorter backoff for timeouts, longer for other errors
          const backoffDelay = isTimeout ? 2000 : Math.pow(2, attempt) * 1000;
          console.log(`⏳ Retrying in ${backoffDelay}ms...`);
          await new Promise(resolve => setTimeout(resolve, backoffDelay));
        }
      }
    }

    return false;
  }

  async injectSEOQuake(page: Page): Promise<boolean> {
    try {
      console.log('💉 Injecting SEOquake functionality...');
      
      // Inject a mock SEOquake object for testing purposes
      await page.evaluateOnNewDocument(() => {
        (window as any).seoQuake = {
          getDomainAuthority: () => Math.floor(Math.random() * 40) + 30, // Mock DA 30-70
          getPageAuthority: () => Math.floor(Math.random() * 30) + 20,   // Mock PA 20-50
          getBacklinks: () => Math.floor(Math.random() * 1000) + 100,    // Mock backlinks
          isReady: () => true,
        };
      });

      console.log('✅ SEOquake mock injected successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to inject SEOquake:', error);
      return false;
    }
  }

  async simulateHumanBehavior(page: Page): Promise<void> {
    try {
      // Random mouse movements
      const randomX = Math.floor(Math.random() * this.config.viewport.width);
      const randomY = Math.floor(Math.random() * this.config.viewport.height);
      await page.mouse.move(randomX, randomY);

      // Random scroll
      const scrollDistance = Math.floor(Math.random() * 500) + 200;
      await page.evaluate((distance) => {
        window.scrollBy(0, distance);
      }, scrollDistance);

      // Random delay
      const delay = Math.random() * 1000 + 500; // 0.5-1.5 seconds
      await new Promise(resolve => setTimeout(resolve, delay));
    } catch (error) {
      console.error('Error simulating human behavior:', error);
    }
  }

  async close(): Promise<void> {
    if (this.browser) {
      console.log('🔒 Closing browser...');
      await this.browser.close();
      this.browser = null;
      this.activePagesCount = 0;
      console.log('✅ Browser closed');
    }
  }

  getStats() {
    return {
      isInitialized: !!this.browser,
      activePagesCount: this.activePagesCount,
      uptime: Date.now() - this.startTime,
      memoryUsage: process.memoryUsage(),
    };
  }

  async healthCheck(): Promise<boolean> {
    try {
      if (!this.browser) {
        return false;
      }

      // Try to create a test page
      const testPage = await this.createPage();
      await testPage.goto('about:blank');
      await this.closePage(testPage);
      
      return true;
    } catch (error) {
      console.error('Browser health check failed:', error);
      return false;
    }
  }
}

// Singleton instance for the browser manager
let browserManagerInstance: BrowserManager | null = null;

export function getBrowserManager(config?: BrowserConfig): BrowserManager {
  if (!browserManagerInstance) {
    if (!config) {
      throw new Error('Browser configuration required for first initialization');
    }
    browserManagerInstance = new BrowserManager(config);
  }
  return browserManagerInstance;
}

export async function closeBrowserManager(): Promise<void> {
  if (browserManagerInstance) {
    await browserManagerInstance.close();
    browserManagerInstance = null;
  }
}
