// Main entry point for the Bun scraping microservice
import express from 'express';
import cors from 'cors';
import WebSocket from 'ws';
import { Server } from 'http';
import dotenv from 'dotenv';
import { join } from 'path';
import { getBrowserManager } from './utils/browser';
import { ServiceConfig, WebSocketMessage } from './types/scraping';

// Load environment variables
dotenv.config({ path: join(__dirname, '../.env') });

// Initialize Express app
const app = express();
app.use(cors());
app.use(express.json());

// Initialize HTTP Server for WebSocket
const server = new Server(app);
const wss = new WebSocket.Server({ server });

const PORT = process.env.PORT || 3000;

// Browser and Service Configurations
const browserConfig = {
  headless: true,
  viewport: { width: 1280, height: 720 },
  timeout: 60000,
  retries: 2,
  stealthMode: true,
  extensionsEnabled: true,
};

const serviceConfig: ServiceConfig = {
  port: PORT as number,
  pythonBackendUrl: process.env.PYTHON_BACKEND_URL || 'http://localhost:8001',
  browser: browserConfig,
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

// Initialize Browser Manager
const browserManager = getBrowserManager(serviceConfig.browser);

(async () => {
  await browserManager.initialize();

  // Health Check Route
  app.get('/health', async (_, res) => {
    const health = await browserManager.healthCheck();
    res.status(health ? 200 : 500).json({ status: health ? 'healthy' : 'unhealthy' });
  });

  // WebSocket Connection
  wss.on('connection', (ws: WebSocket) => {
    console.log('📡 WebSocket client connected');

    ws.on('message', (message: string) => {
      console.log('Received:', message);
      // Parse and handle WebSocket messages
      const msg: WebSocketMessage = JSON.parse(message);
      handleWebSocketMessage(ws, msg);
    });

    ws.send(JSON.stringify({ type: 'status_update', message: 'Connected to Bun scraping service' }));
  });

  // Start the HTTP server
  server.listen(PORT, () => {
    console.log(`🚀 Bun scraping service running on http://localhost:${PORT}`);
  });
})().catch(err => {
  console.error('Failed to initialize Bun server:', err);
});

// Function to handle WebSocket messages
function handleWebSocketMessage(ws: WebSocket, msg: WebSocketMessage) {
  switch (msg.type) {
    case 'progress_update':
      console.log(`Progress on task ${msg.taskId}:`, msg.data);
      break;
    case 'task_completed':
      console.log(`Task ${msg.taskId} completed!`, msg.data);
      break;
    case 'task_failed':
      console.log(`Task ${msg.taskId} failed:`, msg.data);
      break;
    default:
      console.warn('Unknown message type:', msg.type);
  }
}
