"""
CrewAI KP Bot - Simple FastAPI Application for Authentication Testing
===================================================================

Simplified FastAPI application focused on authentication functionality.
"""

from fastapi import FastAPI, WebSocket
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
        "http://localhost:3001",  # Frontend dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
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
    from src.api.routes.auth_new import router as auth_router
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

# Include Blog Research Routes
try:
    from src.api.routes.blogs_real import router as blogs_router
    app.include_router(blogs_router, tags=["Blog Research"])
    logger.info("✅ Blog research routes loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import blog research routes: {e}")

# Include Comment Generation Routes
try:
    from src.api.routes.comments import router as comments_router
    app.include_router(comments_router, prefix="/api/comments", tags=["Comment Generation"])
    logger.info("✅ Comment generation routes loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import comment generation routes: {e}")

# Include WebSocket support
try:
    from src.api.websocket import websocket_manager
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        user_id = "anonymous"  # In real case, retrieve this from session or token
        # Subscribe to tasks channel for real-time updates
        channels = ["general", "tasks"]
        await websocket_manager.connect(websocket, user_id=user_id, channels=channels)
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back for now - in real implementation, handle specific messages
                await websocket.send_text(f"Message received: {data}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await websocket_manager.disconnect(websocket)
    
    logger.info("✅ WebSocket support loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import WebSocket support: {e}")

# Dashboard endpoint with real data
@app.get("/api/dashboard/data")
async def get_dashboard_data():
    """Dashboard data endpoint - returns REAL data from database and scraping service."""
    try:
        # Import database modules
        import sqlite3
        import requests
        from datetime import datetime, timedelta
        
        # Connect to the real database
        db_path = "seo_automation.db"
        dashboard_data = {
            "activeCampaigns": 0,
            "blogsDiscovered": 0,
            "commentsGenerated": 0,
            "successRate": 0.0,
            "recentCampaigns": [],
            "topBlogs": []
        }
        
        # Initialize variables
        blogs_discovered = 0
        comments_generated = 0
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get real metrics from database
            
            # 1. Active Campaigns (distinct research sessions in last 30 days)
            cursor.execute("""
                SELECT COUNT(DISTINCT id) FROM agent_executions 
                WHERE started_at >= datetime('now', '-30 days')
                AND (status = 'running' OR status = 'completed')
            """)
            active_campaigns = cursor.fetchone()[0] or 0
            
            # 2. Blogs Discovered (total blog posts)
            cursor.execute("SELECT COUNT(*) FROM blog_posts")
            blogs_discovered = cursor.fetchone()[0] or 0
            
            # 3. Comments Generated
            cursor.execute("SELECT COUNT(*) FROM comments WHERE status IN ('generated', 'posted')")
            comments_generated = cursor.fetchone()[0] or 0
            
            # 4. Success Rate (posted vs generated comments)
            cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'posted'")
            comments_posted = cursor.fetchone()[0] or 0
            success_rate = (comments_posted / comments_generated * 100) if comments_generated > 0 else 0
            
            # 5. Recent Campaigns (recent blog research activities)
            cursor.execute("""
                SELECT agent_name, context_data, started_at, status,
                       COUNT(*) as execution_count
                FROM agent_executions 
                WHERE started_at >= datetime('now', '-30 days')
                GROUP BY agent_name, DATE(started_at)
                ORDER BY started_at DESC
                LIMIT 5
            """)
            
            recent_campaigns = []
            for row in cursor.fetchall():
                agent_type, parameters, created_at, status, count = row
                campaign_name = f"{agent_type.replace('_', ' ').title()} Campaign"
                if parameters and 'keywords' in str(parameters):
                    # Extract keywords if available
                    try:
                        import json
                        params = json.loads(parameters) if isinstance(parameters, str) else parameters
                        if isinstance(params, dict) and 'keywords' in params:
                            keywords = params['keywords'][:2] if isinstance(params['keywords'], list) else []
                            if keywords:
                                campaign_name += f" - {', '.join(keywords)}"
                    except:
                        pass
                
                recent_campaigns.append({
                    "name": campaign_name[:50],
                    "status": "Active" if status in ['running', 'completed'] else "Paused",
                    "blogs": count
                })
            
            # 6. Top Performing Blogs (extract domain authority from analysis_data JSON)
            cursor.execute("""
                SELECT title, url, analysis_data,
                       (SELECT COUNT(*) FROM comments WHERE post_id = blog_posts.id) as comment_count
                FROM blog_posts 
                WHERE analysis_data IS NOT NULL
                ORDER BY created_at DESC, comment_count DESC
                LIMIT 5
            """)
            
            top_blogs = []
            for row in cursor.fetchall():
                title, url, analysis_data, comments = row
                domain = url.split('/')[2] if '://' in url else url.split('/')[0]
                
                # Extract domain authority from analysis_data JSON
                score = 0
                if analysis_data:
                    try:
                        import json
                        data = json.loads(analysis_data) if isinstance(analysis_data, str) else analysis_data
                        score = data.get('domainAuthority', 0) if isinstance(data, dict) else 0
                    except:
                        score = 0
                
                top_blogs.append({
                    "title": (title or "Untitled Blog Post")[:60],
                    "domain": domain,
                    "score": int(score),
                    "comments": int(comments or 0)
                })
            
            # Update dashboard data with real values
            dashboard_data.update({
                "activeCampaigns": active_campaigns,
                "blogsDiscovered": blogs_discovered,
                "commentsGenerated": comments_generated,
                "successRate": round(success_rate, 1),
                "recentCampaigns": recent_campaigns,
                "topBlogs": top_blogs
            })
            
            conn.close()
            
        except Exception as db_error:
            logger.warning(f"Database error, using fallback data: {db_error}")
            # If database is empty or has issues, provide some meaningful fallback
            dashboard_data = {
                "activeCampaigns": 0,
                "blogsDiscovered": 0,
                "commentsGenerated": 0,
                "successRate": 0.0,
                "recentCampaigns": [
                    {"name": "No campaigns yet - Start your first blog research!", "status": "Ready", "blogs": 0}
                ],
                "topBlogs": [
                    {"title": "No blogs discovered yet - Run blog research to see results", "domain": "kloudportal.com", "score": 0, "comments": 0}
                ]
            }
        
        # Try to get real-time data from scraping service if available
        try:
            scraping_response = requests.get("http://localhost:3002/health", timeout=2)
            if scraping_response.status_code == 200:
                scraping_data = scraping_response.json()
                # Add scraping service status to dashboard
                dashboard_data["scrapingServiceStatus"] = "Online"
                dashboard_data["activeTasks"] = scraping_data.get("websocket", {}).get("activeTasks", 0)
        except:
            dashboard_data["scrapingServiceStatus"] = "Offline"
            dashboard_data["activeTasks"] = 0
        
        return {
            "success": True,
            "message": f"Real dashboard data retrieved successfully (DB: {blogs_discovered} blogs, {comments_generated} comments)",
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return {
            "success": False,
            "message": "Failed to load dashboard data",
            "error": str(e)
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
