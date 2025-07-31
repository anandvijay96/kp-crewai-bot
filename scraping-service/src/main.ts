// Main entry point for the Bun scraping microservice
import express from 'express';
import cors from 'cors';
import WebSocket from 'ws';
import { Server } from 'http';
import dotenv from 'dotenv';
import { join } from 'path';
import { getBrowserManager, closeBrowserManager } from './utils/browser';
import { ServiceConfig, WebSocketMessage } from './types/scraping';
import scrapingRoutes from './routes/scraping';
import { generalRateLimit, requestLogger, requestSizeLimit } from './middleware/rateLimiter';
import { createWebSocketManager, getWebSocketManager } from './services/websocketManager';

// Load environment variables
dotenv.config({ path: join(__dirname, '../.env') });

// Load service configuration
import { getConfig } from './config/config';
const serviceConfig = getConfig();

// Initialize Express app
const app = express();

// Trust proxy for rate limiting
app.set('trust proxy', 1);

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:8000'],
  credentials: true
}));
app.use(requestLogger);
app.use(requestSizeLimit(50)); // 50KB request size limit
app.use(express.json({ limit: '50kb' }));
app.use(express.urlencoded({ extended: true, limit: '50kb' }));

// Initialize HTTP Server for WebSocket
const server = new Server(app);
const wss = new WebSocket.Server({ server });

// Initialize Browser Manager
const browserManager = getBrowserManager(serviceConfig.browser);

// Initialize WebSocket Manager
let wsManager: any;

(async () => {
  await browserManager.initialize();

  // Create WebSocket manager
  wsManager = createWebSocketManager(wss);
  console.log('📡 WebSocket manager initialized');

  // Apply general rate limiting
  app.use(generalRateLimit.middleware());

  // API Routes
  app.use('/api/scraping', scrapingRoutes);

  // Health Check Route
  app.get('/health', async (_, res) => {
    const health = await browserManager.healthCheck();
    const wsStats = wsManager.getStats();
    res.status(health ? 200 : 500).json({ 
      status: health ? 'healthy' : 'unhealthy',
      websocket: wsStats
    });
  });

  // WebSocket Stats Route
  app.get('/api/scraping/ws-stats', async (_, res) => {
    const stats = wsManager.getStats();
    res.json({
      success: true,
      data: stats,
      timestamp: new Date().toISOString()
    });
  });

  // Start the HTTP server
  server.listen(serviceConfig.port, () => {
    console.log(`🚀 Bun scraping service running on http://localhost:${serviceConfig.port}`);
    console.log('💡 Press Ctrl+C to gracefully shutdown');
  });
})().catch(err => {
  console.error('Failed to initialize Bun server:', err);
  process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Received SIGINT (Ctrl+C). Gracefully shutting down...');
  await gracefulShutdown();
});

process.on('SIGTERM', async () => {
  console.log('🛑 Received SIGTERM. Gracefully shutting down...');
  await gracefulShutdown();
});

// Graceful shutdown function
async function gracefulShutdown() {
  console.log('🔄 Starting graceful shutdown...');
  
  try {
    // Close WebSocket manager
    console.log('📡 Closing WebSocket manager...');
    if (wsManager) {
      wsManager.close();
    }
    wss.close();
    
    // Close browser manager
    console.log('🌐 Closing browser manager...');
    await closeBrowserManager();
    
    // Close HTTP server
    console.log('🚪 Closing HTTP server...');
    server.close(() => {
      console.log('✅ HTTP server closed');
      console.log('👋 Graceful shutdown complete. Goodbye!');
      process.exit(0);
    });
    
    // Force exit if graceful shutdown takes too long
    setTimeout(() => {
      console.log('⚠️ Graceful shutdown timeout. Forcing exit...');
      process.exit(1);
    }, 10000); // 10 second timeout
    
  } catch (error) {
    console.error('❌ Error during graceful shutdown:', error);
    process.exit(1);
  }
}

// Export WebSocket manager for use in routes
export function getActiveWebSocketManager() {
  return getWebSocketManager();
}
