"""
CrewAI KP Bot - Test FastAPI Application
=======================================

Simplified FastAPI application for testing Phase 5 implementation.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
from typing import Dict, Any

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
sys.path.append(src_dir)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes with fallback handling
try:
    from routes import auth, campaigns, agents, blogs, comments
    logger.info("✅ Successfully imported all route modules")
except ImportError as e:
    logger.error(f"❌ Failed to import routes: {e}")
    # Create empty router modules for testing
    from fastapi import APIRouter
    
    auth = type('module', (), {'router': APIRouter()})()
    campaigns = type('module', (), {'router': APIRouter()})()
    agents = type('module', (), {'router': APIRouter()})()
    blogs = type('module', (), {'router': APIRouter()})()
    comments = type('module', (), {'router': APIRouter()})()

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API (Test)",
    description="REST API for KloudPortal SEO Blog Commenting Automation - Test Version",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
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
            "details": str(exc)
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
        "service": "CrewAI KP Bot API (Test)",
        "version": "1.0.0-test",
        "message": "API is running successfully!"
    }

# API Info Endpoint
@app.get("/api/info")
async def api_info() -> Dict[str, Any]:
    """
    API information endpoint.
    """
    return {
        "name": "CrewAI KP Bot API (Test)",
        "version": "1.0.0-test",
        "description": "REST API for KloudPortal SEO Blog Commenting Automation - Test Version",
        "features": [
            "Campaign Management",
            "Blog Research", 
            "Comment Generation",
            "Quality Review",
            "Multi-Agent Coordination"
        ],
        "endpoints": {
            "campaigns": "/api/campaigns",
            "agents": "/api/agents", 
            "blogs": "/api/blogs",
            "comments": "/api/comments",
            "auth": "/api/auth"
        },
        "status": "Testing Phase 5 Implementation"
    }

# Test endpoint to verify API functionality
@app.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify API is working.
    """
    return {
        "message": "CrewAI KP Bot API is working correctly!",
        "timestamp": "2025-07-26T10:50:35Z",
        "phase": "Phase 5 - Backend Integration",
        "status": "SUCCESS"
    }

# Include API Routes (with error handling)
try:
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    logger.info("✅ Auth routes included")
except Exception as e:
    logger.warning(f"⚠️ Could not include auth routes: {e}")

try:
    app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"]) 
    logger.info("✅ Campaign routes included")
except Exception as e:
    logger.warning(f"⚠️ Could not include campaign routes: {e}")

try:
    app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
    logger.info("✅ Agent routes included")
except Exception as e:
    logger.warning(f"⚠️ Could not include agent routes: {e}")

try:
    app.include_router(blogs.router, prefix="/api/blogs", tags=["Blog Research"])
    logger.info("✅ Blog routes included")
except Exception as e:
    logger.warning(f"⚠️ Could not include blog routes: {e}")

try:
    app.include_router(comments.router, prefix="/api/comments", tags=["Comment Generation"])
    logger.info("✅ Comment routes included")
except Exception as e:
    logger.warning(f"⚠️ Could not include comment routes: {e}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting CrewAI KP Bot Test API Server...")
    
    # Development server configuration
    uvicorn.run(
        "test_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
