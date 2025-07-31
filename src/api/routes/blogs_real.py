"""
Real-Time Blog Research API Routes - Phase 6 Implementation
Replaces mock data with actual scraping results
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from ...services.integration_service import BunIntegrationService
from ..auth.jwt_handler import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


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
        
        # Start the research process
        result = await bun_service.scrape_url(request.keywords[0])
        task_id = result.get('task_id')

        logger.info(f"Started blog research task {task_id} for user {current_user.get('user_id')}")

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
        progress = blog_scraper.get_progress(task_id)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Research task {task_id} not found"
            )
        
        return BlogProgressResponseModel(**progress)
        
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
        results = blog_scraper.get_results(task_id)
        
        if results is None:
            # Check if task exists
            progress = blog_scraper.get_progress(task_id)
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
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Results not available despite completed status"
                )
        
        # Convert results to response models
        blog_results = []
        for result in results:
            blog_result = BlogResultModel(
                url=result['url'],
                domain=result['domain'],
                title=result['title'],
                description=result['description'],
                domain_authority=result.get('domain_authority'),
                page_authority=result.get('page_authority'),
                category=result.get('category'),
                publish_date=result.get('publish_date'),
                author=result.get('author'),
                content_quality_score=result.get('content_quality_score'),
                comment_opportunities=result.get('comment_opportunities', []),
                discovery_source=result.get('discovery_source', 'unknown'),
                scraped_at=result.get('scraped_at', '')
            )
            blog_results.append(blog_result)
        
        logger.info(f"Retrieved {len(blog_results)} results for task {task_id}")
        return blog_results
        
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
        for task_id in blog_scraper.active_tasks.keys():
            progress = blog_scraper.get_progress(task_id)
            if progress:
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
        progress = blog_scraper.get_progress(task_id)
        
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
        
        # Mark task as cancelled (simplified cancellation)
        if task_id in blog_scraper.active_tasks:
            blog_scraper.active_tasks[task_id].status = "cancelled"
            blog_scraper.active_tasks[task_id].completed_at = progress['started_at']  # Use current time
        
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
        # Get basic stats from the blog scraper
        active_task_count = len(blog_scraper.active_tasks)
        
        # Count tasks by status
        status_counts = {}
        for progress in blog_scraper.active_tasks.values():
            status = progress.status
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
