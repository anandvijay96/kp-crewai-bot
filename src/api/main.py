"""
CrewAI KP Bot - FastAPI Application
===================================

Main FastAPI application for the CrewAI KP Bot SEO automation platform.
Provides REST API endpoints for frontend integration and external access.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import routes and modules with proper paths
try:
    from .routes import auth, agents, campaigns, blogs, comments
    from .routes.auth_new import router as auth_new_router
    from .websocket import websocket_manager
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from routes import campaigns, agents, blogs, comments, auth
    from websocket import websocket_manager

# Import database and logging
try:
    from ..seo_automation.utils.logging import setup_logging
    from ..seo_automation.utils.database import DatabaseManager
except ImportError:
    # Create a simple logging setup for testing
    import logging
    def setup_logging():
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    # Mock database manager for testing
    class DatabaseManager:
        async def connect(self):
            pass
        async def disconnect(self):
            pass

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting CrewAI KP Bot API Server...")
    
    # Initialize database
    try:
        database = DatabaseManager()
        await database.connect()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        # Don't raise in development - continue with mock data
        logger.info("⚠️ Continuing with mock data for development")
    
    # Initialize WebSocket manager
    websocket_manager.startup()
    logger.info("✅ WebSocket manager initialized")
    
    logger.info("🎉 CrewAI KP Bot API Server ready!")
    
    yield
    
    # Shutdown
    logger.info("⏹️ Shutting down CrewAI KP Bot API Server...")
    
    # Close database connections
    try:
        await database.disconnect()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Database shutdown error: {e}")
    
    # Cleanup WebSocket manager
    websocket_manager.shutdown()
    logger.info("✅ WebSocket manager cleaned up")
    
    logger.info("👋 CrewAI KP Bot API Server stopped")

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API",
    description="REST API for KloudPortal SEO Blog Commenting Automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if app.debug else None
        }
    )

# Health Check Endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "service": "CrewAI KP Bot API",
        "version": "1.0.0",
        "timestamp": "2025-07-26T10:41:27Z"
    }

# API Info Endpoint
@app.get("/api/info")
async def api_info() -> Dict[str, Any]:
    """
    API information endpoint.
    """
    return {
        "name": "CrewAI KP Bot API",
        "version": "1.0.0",
        "description": "REST API for KloudPortal SEO Blog Commenting Automation",
        "features": [
            "Campaign Management",
            "Blog Research",
            "Comment Generation",
            "Quality Review",
            "Real-time Updates",
            "Multi-Agent Coordination"
        ],
        "endpoints": {
            "campaigns": "/api/campaigns",
            "agents": "/api/agents",
            "blogs": "/api/blogs",
            "comments": "/api/comments",
            "auth": "/api/auth",
            "websocket": "/ws"
        }
    }

# Include API Routes
app.include_router(auth.router, prefix="/api/auth_old", tags=["Authentication (Legacy)"])
app.include_router(auth_new_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["Blog Research"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comment Generation"])

# WebSocket Endpoint  
# Import the websocket app and mount it
try:
    from .websocket import websocket_app
    app.mount("/ws", websocket_app)
except ImportError:
    # Fallback - create a simple websocket endpoint
    logger.warning("Could not import websocket_app, WebSocket features disabled")

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
