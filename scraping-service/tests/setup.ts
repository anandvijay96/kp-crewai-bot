// Test setup and global utilities
import { config } from 'dotenv';

// Load test environment variables
config({ path: '.env.test' });

// Set test environment variables if not already set
if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = 'test';
}

// Mock browser for tests that don't need real browser
export const mockBrowserManager = {
  createPage: jest.fn(),
  navigateWithRetry: jest.fn(),
  injectSEOQuake: jest.fn(),
  closePage: jest.fn(),
  getStats: jest.fn(),
  initialize: jest.fn(),
  isInitialized: jest.fn(),
  close: jest.fn(),
};

// Test URLs for scraping tests
export const testUrls = {
  article: 'https://dev.to/test-article',
  blog: 'https://medium.com/test-blog',
  product: 'https://example-store.com/product/123',
  documentation: 'https://docs.example.com/api',
  simple: 'https://example.com',
  invalid: 'https://invalid-url-that-does-not-exist.com',
};

// Mock HTML content for different content types
export const mockHtmlContent = {
  article: `
    <html>
      <head>
        <title>Test Article Title</title>
        <meta name="description" content="Test article description">
        <meta property="og:title" content="Test Article Title">
      </head>
      <body>
        <article>
          <h1>Test Article Title</h1>
          <p>This is the main content of the test article. It contains valuable information about testing web scraping functionality.</p>
          <p>Another paragraph with more content to test content extraction.</p>
        </article>
        <nav>
          <a href="/home">Home</a>
          <a href="https://external.com">External Link</a>
        </nav>
      </body>
    </html>
  `,
  blog: `
    <html>
      <head>
        <title>Blog Post Title</title>
        <meta name="description" content="Blog post description">
      </head>
      <body>
        <div class="blog-content">
          <h1>Blog Post Title</h1>
          <div class="post-content">
            <p>This is a blog post content with multiple paragraphs.</p>
            <p>It should be extracted properly by the scraper.</p>
          </div>
        </div>
      </body>
    </html>
  `,
  product: `
    <html>
      <head>
        <title>Product Name - Store</title>
      </head>
      <body>
        <div class="product">
          <h1 class="product-title">Test Product</h1>
          <div class="product-description">
            <p>This is a detailed product description.</p>
            <p>It includes features and benefits.</p>
          </div>
          <div class="price">$99.99</div>
          <button class="add-to-cart">Add to Cart</button>
        </div>
      </body>
    </html>
  `,
};

// Global test helpers
global.beforeAll(async () => {
  // Global setup if needed
});

global.afterAll(async () => {
  // Global cleanup if needed
});
