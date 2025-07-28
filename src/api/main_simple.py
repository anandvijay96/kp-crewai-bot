"""
CrewAI KP Bot - Simple FastAPI Application for Authentication Testing
===================================================================

Simplified FastAPI application focused on authentication functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API - Authentication Test",
    description="Simplified API for testing authentication functionality",
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
        "service": "CrewAI KP Bot API - Auth Test",
        "version": "1.0.0"
    }

# Include Authentication Routes
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from routes.auth_new import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    logger.info("✅ Authentication routes loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import authentication routes: {e}")
    
    # Create a simple test route as fallback
    @app.get("/api/auth/health")
    async def auth_health():
        return {
            "status": "healthy",
            "service": "Authentication System",
            "error": "Routes not properly loaded"
        }

# Basic API info endpoint
@app.get("/api/info")
async def api_info() -> Dict[str, Any]:
    """API information endpoint."""
    return {
        "name": "CrewAI KP Bot API - Auth Test",
        "version": "1.0.0",
        "description": "Simplified API for testing authentication",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",
            "docs": "/docs"
        }
    }

# Debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all registered routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'N/A')
            })
    return {
        "total_routes": len(routes),
        "routes": routes
    }

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
