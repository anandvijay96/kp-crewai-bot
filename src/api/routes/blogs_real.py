"""
Real-Time Blog Research API Routes - Phase 6 Implementation
Replaces mock data with actual scraping results
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import uuid
import asyncio
from datetime import datetime
from urllib.parse import urlparse

from src.api.services.integration_service import BunIntegrationService
from src.api.auth.jwt_handler import get_current_user
from src.api.websocket import notify_task_progress, websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blogs", tags=["blogs"])

# Global task tracking for simplified implementation
_active_tasks = {}


async def _execute_blog_research_task(task_id: str, search_query: str, request: "BlogResearchRequestModel", bun_service: BunIntegrationService, user_id: str):
    """
    Background task to perform blog discovery and update task progress.
    """
    try:
        logger.info(f"Executing blog research task {task_id}...")
        
        # Store task in global tracking
        _active_tasks[task_id] = {
            'status': 'running',
            'progress_percentage': 0.1,
            'current_step': 'Starting blog discovery',
            'found_blogs': 0,
            'validated_blogs': 0,
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': None,
            'errors': []
        }

        # Notify start
        await notify_task_progress(task_id=task_id, task_type='blog_research', progress=0.1, status='starting')

        # Update progress
        _active_tasks[task_id]['progress_percentage'] = 0.3
        _active_tasks[task_id]['current_step'] = 'Searching with Google API'
        
        # Discover blogs using Bun integration
        discovery_results = await bun_service.discover_blogs(search_query, max_results=request.max_results)

        if not discovery_results.get('success'):
            raise Exception(discovery_results.get('error', discovery_results.get('message', "Unknown error")))

        # Extract blogs from the nested data structure
        data = discovery_results.get('data', {})
        blogs = data.get('blogs', []) if isinstance(data, dict) else []
        _active_tasks[task_id]['found_blogs'] = len(blogs)
        _active_tasks[task_id]['progress_percentage'] = 0.7
        _active_tasks[task_id]['current_step'] = f'Found {len(blogs)} blogs'

        # Notify discovery completion
        await notify_task_progress(task_id=task_id, task_type='blog_research', progress=0.7, status='discovery_complete')

        # Process and store the blog results
        processed_blogs = []
        for blog in blogs:
            processed_blog = {
                "url": blog.get('url', ''),
                "domain": blog.get('domain', ''),
                "title": blog.get('title', ''),
                "description": blog.get('snippet', ''),
                "domain_authority": blog.get('domainAuthority', 0),
                "page_authority": blog.get('pageAuthority', 0),
                "category": "blog",
                "publish_date": None,
                "author": None,
                "content_quality_score": 0.8,  # Default score
                "comment_opportunities": ["General engagement"],
                "discovery_source": "google_search",
                "scraped_at": datetime.utcnow().isoformat()
            }
            processed_blogs.append(processed_blog)
        
        _active_tasks[task_id]['validated_blogs'] = len(blogs)
        _active_tasks[task_id]['results'] = processed_blogs  # Store the actual results
        _active_tasks[task_id]['progress_percentage'] = 1.0
        _active_tasks[task_id]['current_step'] = 'Complete'
        _active_tasks[task_id]['status'] = 'completed'
        _active_tasks[task_id]['completed_at'] = datetime.utcnow().isoformat()

        # Notify task completion
        await notify_task_progress(task_id=task_id, task_type='blog_research', progress=1.0, status='completed')

        logger.info(f"Completed blog research task {task_id}. Found {len(blogs)} blogs.")
    except Exception as e:
        logger.error(f"Blog research task {task_id} failed: {str(e)}")
        _active_tasks[task_id] = {
            'status': 'failed',
            'progress_percentage': 1.0,
            'current_step': 'Failed',
            'found_blogs': 0,
            'validated_blogs': 0,
            'started_at': _active_tasks.get(task_id, {}).get('started_at', datetime.utcnow().isoformat()),
            'completed_at': datetime.utcnow().isoformat(),
            'errors': [str(e)]
        }
        await notify_task_progress(task_id=task_id, task_type='blog_research', progress=1.0, status='failed')


class BlogResearchRequestModel(BaseModel):
    """Request model for blog research"""
    keywords: List[str] = Field(..., min_items=1, max_items=10)
    min_domain_authority: int = Field(30, ge=0, le=100)
    min_page_authority: int = Field(25, ge=0, le=100)
    max_results: int = Field(50, ge=1, le=100)
    categories: Optional[List[str]] = None
    language: str = Field("en", max_length=5)
    region: str = Field("US", max_length=5)
    exclude_domains: Optional[List[str]] = None


class BlogResearchResponseModel(BaseModel):
    """Response model for blog research"""
    task_id: str
    status: str
    message: str


class BlogProgressResponseModel(BaseModel):
    """Response model for research progress"""
    task_id: str
    status: str
    progress_percentage: float
    current_step: str
    found_blogs: int
    validated_blogs: int
    started_at: str
    completed_at: Optional[str]
    errors: List[str]


class BlogResultModel(BaseModel):
    """Model for individual blog result"""
    url: str
    domain: str
    title: str
    description: str
    domain_authority: Optional[int]
    page_authority: Optional[int]
    category: Optional[str]
    publish_date: Optional[str]
    author: Optional[str]
    content_quality_score: Optional[float]
    comment_opportunities: List[str]
    discovery_source: str
    scraped_at: str


@router.post("/research", response_model=BlogResearchResponseModel)
async def start_blog_research(
    request: BlogResearchRequestModel,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Start real-time blog research process
    Replaces the mock test API with actual scraping
    """
    try:
        # Initialize Bun integration service
        bun_service = BunIntegrationService()
        
        # Generate task ID for tracking
        task_id = f"blog-research-{uuid.uuid4()}"
        
        # Start real-time blog discovery using Google Search API
        search_query = f"{' '.join(request.keywords)} blog site:*.com OR site:*.org"
        
        # Start background task for blog discovery and analysis
        background_tasks.add_task(
            _execute_blog_research_task,
            task_id=task_id,
            search_query=search_query,
            request=request,
            bun_service=bun_service,
            user_id=current_user.get('user_id')
        )

        logger.info(f"Started blog research task {task_id} for user {current_user.get('user_id')} with query: {search_query}")

        return BlogResearchResponseModel(
            task_id=task_id,
            status="started",
            message=f"Blog research started for keywords: {', '.join(request.keywords)}"
        )
    except Exception as e:
        logger.error(f"Failed to start blog research: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start blog research: {str(e)}"
        )


@router.get("/research/{task_id}/progress", response_model=BlogProgressResponseModel)
async def get_research_progress(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get progress of a blog research task
    """
    try:
        progress = _active_tasks.get(task_id)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Research task {task_id} not found"
            )
        
        return BlogProgressResponseModel(task_id=task_id, **progress)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get research progress for {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research progress: {str(e)}"
        )


@router.get("/research/{task_id}/results", response_model=List[BlogResultModel])
async def get_research_results(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get results of a completed blog research task
    """
    try:
        # Check if task exists
        progress = _active_tasks.get(task_id)
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Research task {task_id} not found"
            )
        elif progress['status'] != 'completed':
            raise HTTPException(
                status_code=202,
                detail=f"Research task {task_id} is not yet completed. Status: {progress['status']}"
            )
        
        # Return the stored results from the completed task
        results = progress.get('results', [])
        logger.info(f"Returning {len(results)} blog results for task {task_id}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get research results for {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research results: {str(e)}"
        )


@router.get("/research/tasks")
async def list_research_tasks(
    current_user = Depends(get_current_user)
):
    """
    List all active research tasks for monitoring
    """
    try:
        # Get all active tasks
        active_tasks = []
        for task_id, progress in _active_tasks.items():
            active_tasks.append({
                "task_id": task_id,
                "status": progress["status"],
                "progress_percentage": progress["progress_percentage"],
                "started_at": progress["started_at"]
            })
        
        return {
            "active_tasks": active_tasks,
            "total_tasks": len(active_tasks)
        }
        
    except Exception as e:
        logger.error(f"Failed to list research tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list research tasks: {str(e)}"
        )


@router.delete("/research/{task_id}")
async def cancel_research_task(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """
    Cancel a running research task
    """
    try:
        progress = _active_tasks.get(task_id)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Research task {task_id} not found"
            )
        
        if progress['status'] in ['completed', 'failed']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel task with status: {progress['status']}"
            )
        
        # Mark task as cancelled
        _active_tasks[task_id]['status'] = "cancelled"
        _active_tasks[task_id]['completed_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Cancelled research task {task_id}")
        
        return {
            "message": f"Research task {task_id} has been cancelled",
            "task_id": task_id,
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel research task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel research task: {str(e)}"
        )


@router.get("/stats")
async def get_scraping_stats(
    current_user = Depends(get_current_user)
):
    """
    Get scraping service statistics
    """
    try:
        # Get basic stats from active tasks
        active_task_count = len(_active_tasks)
        
        # Count tasks by status
        status_counts = {}
        for progress in _active_tasks.values():
            status = progress['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "active_tasks": active_task_count,
            "task_status_breakdown": status_counts,
            "scraping_enabled": True,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scraping stats: {str(e)}"
        )


@router.get("/historical")
async def get_historical_blogs(
    page: int = 1,
    page_size: int = 10,
    current_user = Depends(get_current_user)
):
    """
    Get previously discovered blogs with pagination
    """
    try:
        import sqlite3
        import json
        from datetime import datetime
        
        # Connect to database
        conn = sqlite3.connect('seo_automation.db')
        cursor = conn.cursor()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM blog_posts')
        total_count = cursor.fetchone()[0]
        
        # Get paginated blogs
        cursor.execute('''
            SELECT id, url, title, content_summary, has_comments, analysis_data, status, created_at 
            FROM blog_posts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        
        rows = cursor.fetchall()
        
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
        
        return {
            "success": True,
            "data": {
                "blogs": blogs,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get historical blogs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get historical blogs: {str(e)}"
        )
