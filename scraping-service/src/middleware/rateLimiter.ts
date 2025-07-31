// Rate limiting and validation middleware
import { Request, Response, NextFunction } from 'express';

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

class RateLimiter {
  private store: RateLimitStore = {};
  private readonly windowMs: number;
  private readonly maxRequests: number;
  private readonly cleanupInterval: NodeJS.Timeout;

  constructor(windowMs: number = 60000, maxRequests: number = 100) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
    
    // Clean up expired entries every minute
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60000);
  }

  private cleanup() {
    const now = Date.now();
    Object.keys(this.store).forEach(key => {
      if (this.store[key].resetTime < now) {
        delete this.store[key];
      }
    });
  }

  private getClientId(req: Request): string {
    // Use IP address as client identifier
    return req.ip || req.connection.remoteAddress || 'unknown';
  }

  middleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      const clientId = this.getClientId(req);
      const now = Date.now();
      
      // Initialize or get client data
      if (!this.store[clientId] || now > this.store[clientId].resetTime) {
        this.store[clientId] = {
          count: 0,
          resetTime: now + this.windowMs
        };
      }

      const clientData = this.store[clientId];
      
      // Check if limit exceeded
      if (clientData.count >= this.maxRequests) {
        return res.status(429).json({
          success: false,
          error: 'Too many requests, please try again later.',
          details: {
            limit: this.maxRequests,
            windowMs: this.windowMs,
            resetTime: clientData.resetTime
          },
          timestamp: new Date().toISOString()
        });
      }

      // Increment counter
      clientData.count++;
      
      // Add rate limit headers
      res.set({
        'X-RateLimit-Limit': this.maxRequests.toString(),
        'X-RateLimit-Remaining': (this.maxRequests - clientData.count).toString(),
        'X-RateLimit-Reset': Math.ceil(clientData.resetTime / 1000).toString()
      });

      next();
    };
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

// Create rate limiters for different endpoints
export const generalRateLimit = new RateLimiter(60000, 100); // 100 requests per minute
export const scrapingRateLimit = new RateLimiter(60000, 20);  // 20 scraping requests per minute
export const batchRateLimit = new RateLimiter(300000, 5);     // 5 batch requests per 5 minutes

// Request logging middleware
export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const clientId = req.ip || req.connection.remoteAddress || 'unknown';
  
  // Generate unique request ID
  const requestId = generateRequestId();
  (req as any).requestId = requestId;
  res.set('X-Request-ID', requestId);
  
  console.log(`📡 ${req.method} ${req.path} - Client: ${clientId}`);
  
  // Log response time when request completes
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`📡 ${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
  });
  
  next();
};

// Simple UUID v4 generator
function generateRequestId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Request size limiter
export const requestSizeLimit = (maxSizeKb: number = 10) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const contentLength = parseInt(req.get('content-length') || '0');
    const maxSizeBytes = maxSizeKb * 1024;
    
    if (contentLength > maxSizeBytes) {
      return res.status(413).json({
        success: false,
        error: 'Request payload too large',
        details: {
          maxSize: `${maxSizeKb}KB`,
          receivedSize: `${Math.round(contentLength / 1024)}KB`
        },
        timestamp: new Date().toISOString()
      });
    }
    
    next();
  };
};
