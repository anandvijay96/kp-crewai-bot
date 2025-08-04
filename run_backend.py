"""
CrewAI KP Bot - Backend Runner
============================

Simple backend server runner that works around import path issues.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API",
    description="REST API for KloudPortal SEO Blog Commenting Automation",
    version="1.0.0",
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

# Health Check Endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify API status."""
    return {
        "status": "healthy",
        "service": "CrewAI KP Bot API",
        "version": "1.0.0"
    }

# API Info Endpoint
@app.get("/api/info")
async def api_info() -> Dict[str, Any]:
    """API information endpoint."""
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
            "Multi-Agent Coordination",
            "Task Management",
            "User Authentication",
            "Role-based Access Control"
        ],
        "endpoints": {
            "health": "/health",
            "info": "/api/info",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CrewAI KP Bot API is running!",
        "docs": "/docs",
        "health": "/health"
    }

# Try to import and include routes
def setup_routes():
    """Setup API routes with error handling."""
    try:
        # Try to import routes with absolute imports
        from api.routes.auth_new import router as auth_router
        app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"]) 
        logger.info("✅ Authentication routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load authentication routes: {e}")
        
        # Add basic auth endpoints as fallback
        @app.get("/api/auth/health")
        async def auth_health():
            return {"status": "healthy", "service": "Authentication System"}
    
    try:
        from api.routes.campaigns import router as campaigns_router
        app.include_router(campaigns_router, prefix="/api/campaigns", tags=["Campaigns"])
        logger.info("✅ Campaign routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load campaign routes: {e}")
        
    try:
        from api.routes.agents import router as agents_router
        app.include_router(agents_router, prefix="/api/agents", tags=["Agents"])
        logger.info("✅ Agent routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load agent routes: {e}")
        
    try:
        from api.routes.blogs_real import router as blogs_router
        app.include_router(blogs_router, prefix="/api/blogs", tags=["Blog Research"])
        logger.info("✅ Real blog routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load real blog routes: {e}")
        # Fallback to mock blogs if real routes fail
        try:
            from api.routes.blogs import router as blogs_router
            app.include_router(blogs_router, prefix="/api/blogs", tags=["Blog Research"])
            logger.info("✅ Mock blog routes loaded as fallback")
        except ImportError as e2:
            logger.warning(f"⚠️ Could not load mock blog routes either: {e2}")
        
    try:
        from api.routes.dashboard_real import router as dashboard_router
        app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
        logger.info("✅ Real dashboard routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load real dashboard routes: {e}")
        # Fallback to mock dashboard if real routes fail
        try:
            from api.routes.dashboard import router as dashboard_router
            app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
            logger.info("✅ Mock dashboard routes loaded as fallback")
        except ImportError as e2:
            logger.warning(f"⚠️ Could not load mock dashboard routes either: {e2}")
        
    try:
        from api.routes.comments import router as comments_router
        app.include_router(comments_router, prefix="/api/comments", tags=["Comment Generation"])
        logger.info("✅ Comment routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load comment routes: {e}")
        
    try:
        from api.routes.tasks import router as tasks_router
        app.include_router(tasks_router, prefix="/api/tasks", tags=["Task Management"])
        logger.info("✅ Task routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Could not load task routes: {e}")

# Setup routes on startup
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("🚀 Starting CrewAI KP Bot API Server...")
    
    # Initialize database if needed
    try:
        from simple_db_init import create_tables
        create_tables()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {e}")
    
    setup_routes()
    logger.info("🎉 CrewAI KP Bot API Server ready!")

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    logger.info("Starting server on http://127.0.0.1:8000")
    uvicorn.run(
        "run_backend:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
