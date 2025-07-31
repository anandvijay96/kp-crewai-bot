// Configuration management for the scraping service
import { BrowserConfig, ServiceConfig } from '../types/scraping';

// Default browser configuration
export const defaultBrowserConfig: BrowserConfig = {
  headless: true,
  viewport: { width: 1280, height: 720 },
  timeout: 90000, // Increased from 60s to 90s
  retries: 3, // Increased from 2 to 3
  stealthMode: true,
  extensionsEnabled: true,
};

// Default service configuration
export const defaultServiceConfig: ServiceConfig = {
  port: parseInt(process.env.PORT || '3001', 10),
  pythonBackendUrl: process.env.PYTHON_BACKEND_URL || 'http://localhost:8001',
  browser: defaultBrowserConfig,
  rateLimit: {
    requestsPerSecond: 2,
    requestsPerMinute: 120,
    requestsPerHour: 1000,
    burstLimit: 10,
    cooldownPeriod: 2000,
  },
  searchEngines: {
    google: {
      apiKey: process.env.GOOGLE_API_KEY,
      searchEngineId: process.env.GOOGLE_CSE_ID,
      dailyLimit: 100,
    },
    bing: {
      apiKey: process.env.BING_API_KEY,
      monthlyLimit: 3000,
    },
    duckduckgo: {
      enabled: true,
      maxConcurrent: 5,
    },
  },
  seoQuake: {
    enabled: true,
    extensionPath: './extensions',
    timeout: 10000,
  },
};

// Test configuration
export const testBrowserConfig: BrowserConfig = {
  headless: true,
  viewport: { width: 1280, height: 720 },
  timeout: 10000,
  retries: 1,
  stealthMode: false,
  extensionsEnabled: false,
};

// Get configuration based on environment
export function getConfig(): ServiceConfig {
  const isTest = process.env.NODE_ENV === 'test';
  
  if (isTest) {
    return {
      ...defaultServiceConfig,
      browser: testBrowserConfig,
      rateLimit: {
        ...defaultServiceConfig.rateLimit,
        requestsPerSecond: 10, // More lenient for tests
        requestsPerMinute: 600,
      }
    };
  }
  
  return defaultServiceConfig;
}
