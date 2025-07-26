#!/usr/bin/env python3
"""
Minimal API Server - Phase 5 Backend Integration
================================================

A minimal working FastAPI server for testing backend integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API - Minimal",
    description="Minimal REST API for KloudPortal SEO Blog Commenting Automation",
    version="1.0.0-minimal",
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
        "service": "CrewAI KP Bot API - Minimal",
        "version": "1.0.0-minimal",
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "Phase 5 - Backend Integration",
        "features": [
            "Basic Health Check",
            "CORS Configuration", 
            "API Documentation",
            "Ready for Frontend Integration"
        ]
    }

# API Info Endpoint
@app.get("/api/info")
async def api_info() -> Dict[str, Any]:
    """API information endpoint."""
    return {
        "name": "CrewAI KP Bot API - Minimal",
        "version": "1.0.0-minimal",
        "description": "Minimal REST API for KloudPortal SEO Blog Commenting Automation",
        "phase": "Phase 5 - Backend Integration",
        "status": "Development - Minimal Implementation",
        "endpoints": {
            "health": "/health",
            "info": "/api/info",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "next_steps": [
            "Test frontend connectivity",
            "Add authentication",
            "Integrate with AI agents",
            "Add WebSocket support"
        ]
    }

# Test endpoint for frontend integration
@app.get("/api/test")
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint for frontend integration testing."""
    return {
        "message": "Backend API is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "ready_for_frontend": True,
        "test_data": {
            "campaigns": 2,
            "blogs_discovered": 45,
            "comments_generated": 123,
            "quality_score": 0.85
        }
    }

# Mock campaign endpoint for frontend testing
@app.get("/api/campaigns")
async def list_campaigns() -> Dict[str, Any]:
    """Mock campaigns endpoint for frontend testing."""
    mock_campaigns = [
        {
            "id": "campaign-1",
            "name": "SEO Campaign 1",
            "description": "Test campaign for blog commenting",
            "status": "completed",
            "keywords": ["SEO", "digital marketing"],
            "created_at": datetime.utcnow().isoformat(),
            "progress": 1.0,
            "estimated_cost": 15.50
        },
        {
            "id": "campaign-2",
            "name": "Content Marketing Campaign", 
            "description": "Automated commenting for content marketing",
            "status": "running",
            "keywords": ["content marketing", "automation"],
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0.65,
            "estimated_cost": 22.30
        }
    ]
    
    return {
        "success": True,
        "message": "Campaigns retrieved successfully",
        "campaigns": mock_campaigns,
        "total": len(mock_campaigns),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting CrewAI KP Bot Minimal API Server...")
    print("📋 Phase 5: Backend Integration - Testing Mode")
    print("🌐 API Documentation: http://127.0.0.1:8000/docs")
    print("🏥 Health Check: http://127.0.0.1:8000/health")
    
    # Development server configuration
    uvicorn.run(
        "test_api_minimal:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
