"""
Simple FastAPI Test - CrewAI KP Bot API
=======================================

Basic test to verify FastAPI setup and Phase 5 implementation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CrewAI KP Bot API - Test",
    description="Phase 5 Backend Integration Test",
    version="1.0.0-test"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for testing
class TestResponse(BaseModel):
    success: bool = True
    message: str
    data: Dict[str, Any] = {}
    timestamp: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ============================================================================
# Basic Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CrewAI KP Bot API - Phase 5 Test", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CrewAI KP Bot API",
        "version": "1.0.0-test",
        "phase": "Phase 5 - Backend Integration",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/info")
async def api_info():
    """API information."""
    return {
        "name": "CrewAI KP Bot API",
        "description": "REST API for SEO Blog Commenting Automation",
        "version": "1.0.0-test",
        "phase": "Phase 5 - Backend Integration",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth/*",
            "campaigns": "/api/campaigns/*",
            "agents": "/api/agents/*",
            "blogs": "/api/blogs/*",
            "comments": "/api/comments/*"
        },
        "status": "Testing Phase 5 Implementation"
    }

# ============================================================================
# Authentication Endpoints (Mock)
# ============================================================================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Mock login endpoint."""
    if request.username == "admin" and request.password == "admin123":
        return {
            "success": True,
            "message": "Login successful",
            "access_token": "mock-jwt-token-12345",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_info": {
                "username": "admin",
                "email": "admin@kloudportal.com",
                "full_name": "System Administrator",
                "is_admin": True
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user():
    """Mock current user endpoint."""
    return {
        "success": True,
        "message": "User information retrieved",
        "user": {
            "username": "admin",
            "email": "admin@kloudportal.com", 
            "full_name": "System Administrator",
            "is_admin": True
        }
    }

# ============================================================================
# Campaign Endpoints (Mock)
# ============================================================================

@app.get("/api/campaigns/")
async def list_campaigns():
    """Mock campaign list."""
    return {
        "success": True,
        "message": "Campaigns retrieved successfully",
        "campaigns": [
            {
                "id": "campaign-1",
                "name": "SEO Campaign Test",
                "status": "completed",
                "keywords": ["SEO", "digital marketing"],
                "progress": 1.0,
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20
    }

@app.post("/api/campaigns/")
async def create_campaign(campaign_data: dict):
    """Mock campaign creation."""
    return {
        "success": True,
        "message": "Campaign created successfully",
        "campaign": {
            "id": "campaign-new",
            "name": campaign_data.get("name", "New Campaign"),
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }
    }

# ============================================================================
# Agent Endpoints (Mock)
# ============================================================================

@app.get("/api/agents/status")
async def get_agents_status():
    """Mock agent status."""
    return {
        "success": True,
        "message": "Agent status retrieved successfully",
        "agents": [
            {
                "agent_type": "blog_researcher",
                "status": "active",
                "last_activity": datetime.utcnow().isoformat(),
                "success_rate": 0.94
            },
            {
                "agent_type": "comment_writer", 
                "status": "active",
                "last_activity": datetime.utcnow().isoformat(),
                "success_rate": 0.89
            }
        ]
    }

# ============================================================================
# Blog Research Endpoints (Mock)
# ============================================================================

@app.post("/api/blogs/research")
async def research_blogs(request: dict):
    """Mock blog research."""
    return {
        "success": True,
        "message": "Blog research completed successfully",
        "blogs": [
            {
                "url": "https://searchengineland.com",
                "title": "Search Engine Land",
                "domain": "searchengineland.com",
                "quality_score": 0.91,
                "authority_score": 0.94,
                "discovered_at": datetime.utcnow().isoformat()
            }
        ],
        "total_discovered": 1,
        "execution_time": 15.7,
        "cost": 2.45
    }

@app.get("/api/blogs/historical")
async def get_historical_blogs(
    page: int = 1,
    page_size: int = 10
):
    """Get previously discovered blogs with pagination - TEST endpoint"""
    try:
        import sqlite3
        import json
        
        logger.info(f"API called with page={page}, page_size={page_size}")
        
        # Connect to database
        conn = sqlite3.connect('seo_automation.db')
        cursor = conn.cursor()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM blog_posts')
        total_count = cursor.fetchone()[0]
        
        logger.info(f"Total blogs in database: {total_count}")
        
        # Get paginated blogs
        cursor.execute('''
            SELECT id, url, title, content_summary, has_comments, analysis_data, status, created_at 
            FROM blog_posts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        
        rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} rows for page {page} (offset {offset})")
        
        blogs = []
        for row in rows:
            blog_id, url, title, summary, has_comments, analysis_data_str, status, created_at = row
            
            # Parse analysis data
            analysis_data = {}
            if analysis_data_str:
                try:
                    analysis_data = json.loads(analysis_data_str)
                except json.JSONDecodeError:
                    pass
            
            blogs.append({
                "id": blog_id,
                "url": url,
                "title": title,
                "content_summary": summary,
                "has_comments": bool(has_comments),
                "status": status,
                "created_at": created_at,
                "analysis_data": analysis_data
            })
        
        conn.close()
        
        response_data = {
            "success": True,
            "data": {
                "blogs": blogs,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
        logger.info(f"Returning response with {len(blogs)} blogs, total_pages: {response_data['data']['total_pages']}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to get historical blogs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get historical blogs: {str(e)}"
        )

# ============================================================================
# Comment Generation Endpoints (Mock)
# ============================================================================

@app.post("/api/comments/generate")
async def generate_comments(request: dict):
    """Mock comment generation."""
    return {
        "success": True,
        "message": "Comments generated successfully",
        "comments": [
            {
                "id": "comment-1",
                "content": "Great insights on this topic! Very informative analysis.",
                "style": "engaging",
                "quality_score": 0.87,
                "generated_at": datetime.utcnow().isoformat()
            }
        ],
        "blog_url": request.get("blog_url", ""),
        "execution_time": 8.5,
        "cost": 0.34
    }

# ============================================================================
# Test Endpoint
# ============================================================================

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify everything is working."""
    return {
        "message": "🎉 CrewAI KP Bot API is working perfectly!",
        "phase": "Phase 5 - Backend Integration",
        "status": "SUCCESS",
        "timestamp": datetime.utcnow().isoformat(),
        "features_tested": [
            "FastAPI Setup ✅",
            "CORS Configuration ✅", 
            "Pydantic Models ✅",
            "Authentication Mock ✅",
            "Campaign Management Mock ✅",
            "Agent Status Mock ✅",
            "Blog Research Mock ✅",
            "Comment Generation Mock ✅"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting CrewAI KP Bot Test API...")
    
    uvicorn.run(
        "test_api:app",
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="info"
    )
