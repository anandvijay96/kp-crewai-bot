// TypeScript interfaces for the Bun scraping microservice

export interface BlogPost {
  id?: string;
  url: string;
  title: string;
  content?: string;
  contentSummary?: string;
  author?: string;
  publishDate?: Date;
  keywords?: string[];
  commentCount?: number;
  lastChecked?: Date;
  commentStatus?: 'open' | 'closed' | 'moderated';
  engagementMetrics?: {
    likes?: number;
    shares?: number;
    comments?: number;
  };
}

export interface Blog {
  id?: string;
  url: string;
  domain: string;
  domainAuthority?: number;
  pageAuthority?: number;
  category?: string;
  platformType?: string;
  authRequired?: boolean;
  status?: 'active' | 'inactive' | 'blocked';
  commentingGuidelines?: {
    requiresRegistration?: boolean;
    moderationEnabled?: boolean;
    maxCommentLength?: number;
    allowedTags?: string[];
    bannedWords?: string[];
  };
  submissionSuccessRate?: number;
  lastCrawled?: Date;
  posts?: BlogPost[];
}

export interface AuthorityScore {
  domainAuthority: number;
  pageAuthority: number;
  source: 'seoguake' | 'moz' | 'ahrefs' | 'fallback';
  confidence: number;
  lastUpdated: Date;
  metrics: {
    backlinks?: number;
    referringDomains?: number;
    organicTraffic?: number;
  };
}

export interface SearchEngineResult {
  title: string;
  url: string;
  snippet: string;
  position: number;
  source: 'google' | 'bing' | 'duckduckgo';
}

export interface ScrapingRequest {
  taskId: string;
  type: 'blog_discovery' | 'authority_check' | 'content_analysis' | 'full_research';
  parameters: {
    keywords?: string[];
    category?: string;
    limit?: number;
    minDomainAuthority?: number;
    urls?: string[];
    targetLanguage?: string;
    includeContent?: boolean;
  };
  filters?: {
    excludeDomains?: string[];
    requiredWords?: string[];
    contentType?: 'blog' | 'news' | 'forum' | 'any';
  };
}

export interface ScrapingResult {
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number; // 0-100
  results: {
    blogs?: Blog[];
    posts?: BlogPost[];
    authorityScores?: AuthorityScore[];
    searchResults?: SearchEngineResult[];
  };
  metadata: {
    startTime: Date;
    endTime?: Date;
    totalProcessed: number;
    successCount: number;
    errorCount: number;
    averageResponseTime: number;
  };
  errors?: Array<{
    url: string;
    error: string;
    timestamp: Date;
  }>;
}

export interface BrowserConfig {
  headless: boolean;
  userAgent?: string;
  viewport: {
    width: number;
    height: number;
  };
  timeout: number;
  retries: number;
  proxyConfig?: {
    server: string;
    username?: string;
    password?: string;
  };
  stealthMode: boolean;
  extensionsEnabled: boolean;
}

export interface RateLimitConfig {
  requestsPerSecond: number;
  requestsPerMinute: number;
  requestsPerHour: number;
  burstLimit: number;
  cooldownPeriod: number; // milliseconds
}

export interface WebSocketMessage {
  type: 'progress_update' | 'task_completed' | 'task_failed' | 'status_update';
  taskId: string;
  data: any;
  timestamp: Date;
}

export interface ServiceConfig {
  port: number;
  pythonBackendUrl: string;
  browser: BrowserConfig;
  rateLimit: RateLimitConfig;
  searchEngines: {
    google: {
      apiKey?: string;
      searchEngineId?: string;
      dailyLimit: number;
    };
    bing: {
      apiKey?: string;
      monthlyLimit: number;
    };
    duckduckgo: {
      enabled: boolean;
      maxConcurrent: number;
    };
  };
  seoQuake: {
    enabled: boolean;
    extensionPath?: string;
    timeout: number;
  };
}

export interface ScrapingStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  requestsPerMinute: number;
  activeConnections: number;
  uptime: number;
  memoryUsage: {
    used: number;
    free: number;
    total: number;
  };
  browserInstances: number;
}
