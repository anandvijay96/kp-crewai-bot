"""
WebSocket Manager
================

WebSocket connection management for real-time updates and notifications.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """WebSocket message types."""
    CAMPAIGN_UPDATE = "campaign_update"
    AGENT_STATUS = "agent_status"
    TASK_PROGRESS = "task_progress"
    SYSTEM_NOTIFICATION = "system_notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class WebSocketManager:
    """
    WebSocket connection manager for real-time communication.
    """
    
    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Channel subscriptions (user_id -> list of channels)
        self.subscriptions: Dict[str, List[str]] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    def startup(self):
        """Initialize WebSocket manager."""
        logger.info("🚀 WebSocket manager starting up...")
        
        # Start background tasks
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.background_tasks.append(heartbeat_task)
        
        logger.info("✅ WebSocket manager started successfully")
    
    def shutdown(self):
        """Cleanup WebSocket manager."""
        logger.info("⏹️ WebSocket manager shutting down...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        for user_connections in self.active_connections.values():
            for websocket in user_connections:
                asyncio.create_task(websocket.close())
        
        self.active_connections.clear()
        self.subscriptions.clear()
        self.connection_metadata.clear()
        
        logger.info("✅ WebSocket manager shutdown complete")
    
    async def connect(self, websocket: WebSocket, user_id: str, channels: Optional[List[str]] = None):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            channels: Optional list of channels to subscribe to
        """
        await websocket.accept()
        
        # Add connection
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Set up subscriptions
        if channels:
            self.subscriptions[user_id] = channels
        else:
            self.subscriptions[user_id] = ["general"]  # Default channel
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            "channels": self.subscriptions[user_id]
        }
        
        logger.info(f"✅ WebSocket connected: User {user_id}, Channels: {self.subscriptions[user_id]}")
        
        # Send welcome message
        welcome_message = {
            "type": MessageType.SYSTEM_NOTIFICATION,
            "data": {
                "message": "Connected to CrewAI KP Bot WebSocket",
                "user_id": user_id,
                "channels": self.subscriptions[user_id],
                "server_time": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_to_websocket(websocket, welcome_message)
    
    async def disconnect(self, websocket: WebSocket):
        """
        Handle WebSocket disconnection.
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return
        
        user_id = metadata["user_id"]
        
        # Remove connection
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    if user_id in self.subscriptions:
                        del self.subscriptions[user_id]
            except ValueError:
                pass  # Connection already removed
        
        # Clean up metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"❌ WebSocket disconnected: User {user_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Send message to all connections for a specific user.
        
        Args:
            user_id: Target user ID
            message: Message to send
        """
        if user_id not in self.active_connections:
            logger.warning(f"No active connections for user: {user_id}")
            return
        
        connections = self.active_connections[user_id].copy()
        disconnected = []
        
        for websocket in connections:
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)
    
    async def send_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Send message to all users subscribed to a channel.
        
        Args:
            channel: Target channel
            message: Message to send
        """
        sent_to_users = []
        
        for user_id, channels in self.subscriptions.items():
            if channel in channels:
                await self.send_to_user(user_id, message)
                sent_to_users.append(user_id)
        
        logger.info(f"📡 Broadcast to channel '{channel}': {len(sent_to_users)} users")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message to broadcast
        """
        total_sent = 0
        
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)
            total_sent += 1
        
        logger.info(f"📡 Broadcast message sent to {total_sent} users")
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send message to a specific WebSocket connection.
        
        Args:
            websocket: Target WebSocket
            message: Message to send
        """
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
            raise
    
    async def _heartbeat_loop(self):
        """
        Background task to send periodic heartbeats and check connection health.
        """
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                heartbeat_message = {
                    "type": MessageType.HEARTBEAT,
                    "data": {
                        "server_time": datetime.utcnow().isoformat(),
                        "active_connections": len(self.connection_metadata)
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Send heartbeat to all connections
                for websocket in list(self.connection_metadata.keys()):
                    try:
                        await self._send_to_websocket(websocket, heartbeat_message)
                        # Update last heartbeat time
                        self.connection_metadata[websocket]["last_heartbeat"] = datetime.utcnow()
                    except Exception as e:
                        logger.warning(f"Heartbeat failed for connection: {e}")
                        await self.disconnect(websocket)
                
            except asyncio.CancelledError:
                logger.info("Heartbeat loop cancelled")
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.
        
        Returns:
            dict: Connection statistics
        """
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "unique_users": len(self.active_connections),
            "channels": {
                channel: sum(1 for channels in self.subscriptions.values() if channel in channels)
                for channel in set().union(*self.subscriptions.values()) if self.subscriptions.values()
            },
            "connection_metadata": {
                "oldest_connection": min(
                    (metadata["connected_at"] for metadata in self.connection_metadata.values()),
                    default=None
                ),
                "newest_connection": max(
                    (metadata["connected_at"] for metadata in self.connection_metadata.values()),
                    default=None
                )
            }
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# ============================================================================
# WebSocket Notification Helpers
# ============================================================================

async def notify_campaign_update(campaign_id: str, status: str, progress: float, message: str = ""):
    """
    Send campaign update notification.
    
    Args:
        campaign_id: Campaign identifier
        status: Campaign status
        progress: Progress percentage (0.0 to 1.0)
        message: Optional status message
    """
    notification = {
        "type": MessageType.CAMPAIGN_UPDATE,
        "data": {
            "campaign_id": campaign_id,
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat(),
        "channel": f"campaign_{campaign_id}"
    }
    
    await websocket_manager.send_to_channel(f"campaign_{campaign_id}", notification)

async def notify_agent_status(agent_type: str, status: str, metrics: Dict[str, Any]):
    """
    Send agent status notification.
    
    Args:
        agent_type: Type of agent
        status: Agent status
        metrics: Performance metrics
    """
    notification = {
        "type": MessageType.AGENT_STATUS,
        "data": {
            "agent_type": agent_type,
            "status": status,
            "metrics": metrics,
            "updated_at": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat(),
        "channel": "agents"
    }
    
    await websocket_manager.send_to_channel("agents", notification)

async def notify_task_progress(task_id: str, task_type: str, progress: float, status: str):
    """
    Send task progress notification.
    
    Args:
        task_id: Task identifier
        task_type: Type of task
        progress: Progress percentage (0.0 to 1.0)
        status: Task status
    """
    notification = {
        "type": MessageType.TASK_PROGRESS,
        "data": {
            "task_id": task_id,
            "task_type": task_type,
            "progress": progress,
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat(),
        "channel": "tasks"
    }
    
    await websocket_manager.send_to_channel("tasks", notification)

async def notify_system_event(event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
    """
    Send system-wide notification.
    
    Args:
        event_type: Type of system event
        message: Notification message
        data: Optional additional data
    """
    notification = {
        "type": MessageType.SYSTEM_NOTIFICATION,
        "data": {
            "event_type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat(),
        "channel": "system"
    }
    
    await websocket_manager.broadcast(notification)

# ============================================================================
# WebSocket Routes
# ============================================================================

from fastapi import FastAPI

# Create WebSocket sub-application
websocket_app = FastAPI()

@websocket_app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time communication.
    
    Query Parameters:
        - user_id: User identification
        - channels: Comma-separated list of channels to subscribe to
    """
    # Get query parameters
    query_params = dict(websocket.query_params)
    user_id = query_params.get("user_id", "anonymous")
    channels_param = query_params.get("channels", "general")
    channels = [ch.strip() for ch in channels_param.split(",")]
    
    try:
        # Connect user
        await websocket_manager.connect(websocket, user_id, channels)
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_client_message(websocket, user_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {user_id}")
                break
            except json.JSONDecodeError:
                error_message = {
                    "type": MessageType.ERROR,
                    "data": {
                        "error": "Invalid JSON format",
                        "message": "Please send valid JSON messages"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket_manager._send_to_websocket(websocket, error_message)
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                error_message = {
                    "type": MessageType.ERROR,
                    "data": {
                        "error": "Message processing failed",
                        "message": str(e)
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket_manager._send_to_websocket(websocket, error_message)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

async def handle_client_message(websocket: WebSocket, user_id: str, message: Dict[str, Any]):
    """
    Handle messages received from WebSocket clients.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        message: Received message
    """
    message_type = message.get("type", "unknown")
    data = message.get("data", {})
    
    logger.info(f"Received WebSocket message from {user_id}: {message_type}")
    
    if message_type == "ping":
        # Respond to ping with pong
        pong_message = {
            "type": "pong",
            "data": {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket_manager._send_to_websocket(websocket, pong_message)
    
    elif message_type == "subscribe":
        # Handle channel subscription
        channels = data.get("channels", [])
        if user_id in websocket_manager.subscriptions:
            websocket_manager.subscriptions[user_id].extend(channels)
            websocket_manager.subscriptions[user_id] = list(set(websocket_manager.subscriptions[user_id]))
        
        response = {
            "type": "subscription_updated",
            "data": {
                "channels": websocket_manager.subscriptions.get(user_id, []),
                "message": f"Subscribed to channels: {channels}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket_manager._send_to_websocket(websocket, response)
    
    elif message_type == "unsubscribe":
        # Handle channel unsubscription
        channels = data.get("channels", [])
        if user_id in websocket_manager.subscriptions:
            for channel in channels:
                if channel in websocket_manager.subscriptions[user_id]:
                    websocket_manager.subscriptions[user_id].remove(channel)
        
        response = {
            "type": "subscription_updated",
            "data": {
                "channels": websocket_manager.subscriptions.get(user_id, []),
                "message": f"Unsubscribed from channels: {channels}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket_manager._send_to_websocket(websocket, response)
    
    elif message_type == "get_stats":
        # Send connection statistics
        stats = websocket_manager.get_connection_stats()
        response = {
            "type": "stats",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket_manager._send_to_websocket(websocket, response)
    
    else:
        # Unknown message type
        error_message = {
            "type": MessageType.ERROR,
            "data": {
                "error": f"Unknown message type: {message_type}",
                "supported_types": ["ping", "subscribe", "unsubscribe", "get_stats"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket_manager._send_to_websocket(websocket, error_message)

# Assign the websocket app to the manager
websocket_manager.app = websocket_app
