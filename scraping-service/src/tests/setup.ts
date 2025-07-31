// Test setup for Jest
import 'jest';

// Global test utilities and mocks
global.console = {
  ...console,
  // Uncomment to ignore specific console methods during tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
};

// Mock environment variables for testing
process.env.NODE_ENV = 'test';
process.env.PORT = '3002';
process.env.PYTHON_BACKEND_URL = 'http://localhost:8001';
process.env.ALLOWED_ORIGINS = 'http://localhost:3000,http://localhost:8000';

// Setup global test timeout
jest.setTimeout(10000);

// Mock browser manager to avoid browser initialization during tests
jest.mock('../utils/browser', () => ({
  getBrowserManager: jest.fn(() => ({
    initialize: jest.fn().mockResolvedValue(undefined),
    healthCheck: jest.fn().mockResolvedValue(true),
    close: jest.fn().mockResolvedValue(undefined),
    createPage: jest.fn().mockResolvedValue({
      goto: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue('mocked content'),
      waitForSelector: jest.fn().mockResolvedValue(undefined),
      close: jest.fn().mockResolvedValue(undefined),
    }),
    navigateWithRetry: jest.fn().mockResolvedValue(true),
    injectSEOQuake: jest.fn().mockResolvedValue(true),
    closePage: jest.fn().mockResolvedValue(undefined),
    getStats: jest.fn().mockReturnValue({
      isInitialized: true,
      activePagesCount: 0,
      uptime: 1000,
      memoryUsage: { rss: 100, heapUsed: 50, heapTotal: 100, external: 10, arrayBuffers: 0 },
    }),
  })),
  closeBrowserManager: jest.fn().mockResolvedValue(undefined),
}));

// Global cleanup
beforeEach(() => {
  jest.clearAllMocks();
});

afterAll(() => {
  jest.restoreAllMocks();
});
