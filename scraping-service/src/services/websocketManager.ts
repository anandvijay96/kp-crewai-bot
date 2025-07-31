// WebSocket Manager for real-time progress updates
import WebSocket from 'ws';
import { WebSocketMessage } from '../types/scraping';
import { v4 as uuidv4 } from 'uuid';

export interface ProgressUpdate {
  taskId: string;
  type: 'blog_discovery' | 'scraping' | 'analysis' | 'completed' | 'failed';
  progress: number; // 0-100
  message: string;
  data?: any;
  timestamp: Date;
}

export class WebSocketManager {
  private clients: Map<string, WebSocket> = new Map();
  private tasks: Map<string, ProgressUpdate> = new Map();

  constructor(private wss: WebSocket.Server) {
    this.setupWebSocketServer();
  }

  private setupWebSocketServer() {
    this.wss.on('connection', (ws: WebSocket) => {
      const clientId = uuidv4();
      this.clients.set(clientId, ws);
      
      console.log(`📡 WebSocket client connected: ${clientId}`);
      
      // Send welcome message
      this.sendToClient(clientId, {
        type: 'status_update',
        taskId: 'system',
        data: { 
          message: 'Connected to Bun scraping service',
          clientId,
          timestamp: new Date()
        },
        timestamp: new Date()
      });

      // Handle incoming messages
      ws.on('message', (message: string) => {
        try {
          const msg: WebSocketMessage = JSON.parse(message);
          this.handleClientMessage(clientId, msg);
        } catch (error) {
          console.error('Invalid WebSocket message:', error);
        }
      });

      // Handle client disconnect
      ws.on('close', () => {
        console.log(`📡 WebSocket client disconnected: ${clientId}`);
        this.clients.delete(clientId);
      });

      ws.on('error', (error) => {
        console.error(`WebSocket error for client ${clientId}:`, error);
        this.clients.delete(clientId);
      });
    });
  }

  private handleClientMessage(clientId: string, msg: WebSocketMessage) {
    console.log(`📨 Message from client ${clientId}:`, msg);
    
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

  // Send message to specific client
  public sendToClient(clientId: string, message: WebSocketMessage): boolean {
    const client = this.clients.get(clientId);
    if (client && client.readyState === WebSocket.OPEN) {
      try {
        client.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error(`Failed to send message to client ${clientId}:`, error);
        this.clients.delete(clientId);
        return false;
      }
    }
    return false;
  }

  // Broadcast message to all connected clients
  public broadcast(message: WebSocketMessage): number {
    let successCount = 0;
    
    this.clients.forEach((client, clientId) => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(JSON.stringify(message));
          successCount++;
        } catch (error) {
          console.error(`Failed to broadcast to client ${clientId}:`, error);
          this.clients.delete(clientId);
        }
      } else {
        // Remove dead connections
        this.clients.delete(clientId);
      }
    });

    return successCount;
  }

  // Start a new task and notify clients
  public startTask(taskId: string, type: ProgressUpdate['type'], message: string): void {
    const update: ProgressUpdate = {
      taskId,
      type,
      progress: 0,
      message,
      timestamp: new Date()
    };
    
    this.tasks.set(taskId, update);
    
    this.broadcast({
      type: 'progress_update',
      taskId,
      data: update,
      timestamp: new Date()
    });

    console.log(`🚀 Task started: ${taskId} - ${message}`);
  }

  // Update task progress
  public updateProgress(taskId: string, progress: number, message: string, data?: any): void {
    const task = this.tasks.get(taskId);
    if (!task) {
      console.warn(`Task not found: ${taskId}`);
      return;
    }

    const update: ProgressUpdate = {
      ...task,
      progress: Math.min(100, Math.max(0, progress)),
      message,
      data,
      timestamp: new Date()
    };

    this.tasks.set(taskId, update);

    this.broadcast({
      type: 'progress_update',
      taskId,
      data: update,
      timestamp: new Date()
    });

    console.log(`📊 Task progress: ${taskId} - ${progress}% - ${message}`);
  }

  // Complete a task
  public completeTask(taskId: string, message: string, data?: any): void {
    const task = this.tasks.get(taskId);
    if (!task) {
      console.warn(`Task not found: ${taskId}`);
      return;
    }

    const update: ProgressUpdate = {
      ...task,
      type: 'completed',
      progress: 100,
      message,
      data,
      timestamp: new Date()
    };

    this.tasks.set(taskId, update);

    this.broadcast({
      type: 'task_completed',
      taskId,
      data: update,
      timestamp: new Date()
    });

    console.log(`✅ Task completed: ${taskId} - ${message}`);

    // Clean up completed task after 5 minutes
    setTimeout(() => {
      this.tasks.delete(taskId);
    }, 5 * 60 * 1000);
  }

  // Fail a task
  public failTask(taskId: string, message: string, error?: any): void {
    const task = this.tasks.get(taskId);
    if (!task) {
      console.warn(`Task not found: ${taskId}`);
      return;
    }

    const update: ProgressUpdate = {
      ...task,
      type: 'failed',
      message,
      data: { error: error?.message || error },
      timestamp: new Date()
    };

    this.tasks.set(taskId, update);

    this.broadcast({
      type: 'task_failed',
      taskId,
      data: update,
      timestamp: new Date()
    });

    console.log(`❌ Task failed: ${taskId} - ${message}`);

    // Clean up failed task after 5 minutes
    setTimeout(() => {
      this.tasks.delete(taskId);
    }, 5 * 60 * 1000);
  }

  // Get current task status
  public getTaskStatus(taskId: string): ProgressUpdate | undefined {
    return this.tasks.get(taskId);
  }

  // Get all active tasks
  public getAllTasks(): ProgressUpdate[] {
    return Array.from(this.tasks.values());
  }

  // Get connection statistics
  public getStats() {
    return {
      connectedClients: this.clients.size,
      activeTasks: this.tasks.size,
      clientIds: Array.from(this.clients.keys()),
      tasks: this.getAllTasks()
    };
  }

  // Clean up completed/failed tasks older than specified time
  public cleanupOldTasks(maxAgeMinutes: number = 10): number {
    const cutoffTime = new Date(Date.now() - maxAgeMinutes * 60 * 1000);
    let cleanedCount = 0;

    this.tasks.forEach((task, taskId) => {
      if (task.timestamp < cutoffTime && (task.type === 'completed' || task.type === 'failed')) {
        this.tasks.delete(taskId);
        cleanedCount++;
      }
    });

    if (cleanedCount > 0) {
      console.log(`🧹 Cleaned up ${cleanedCount} old tasks`);
    }

    return cleanedCount;
  }

  // Close all connections
  public close(): void {
    console.log('📡 Closing WebSocket manager...');
    
    this.clients.forEach((client, clientId) => {
      if (client.readyState === WebSocket.OPEN) {
        client.close();
      }
    });
    
    this.clients.clear();
    this.tasks.clear();
    
    console.log('✅ WebSocket manager closed');
  }
}

// Singleton instance
let wsManager: WebSocketManager | null = null;

export function createWebSocketManager(wss: WebSocket.Server): WebSocketManager {
  if (wsManager) {
    wsManager.close();
  }
  wsManager = new WebSocketManager(wss);
  return wsManager;
}

export function getWebSocketManager(): WebSocketManager | null {
  return wsManager;
}
