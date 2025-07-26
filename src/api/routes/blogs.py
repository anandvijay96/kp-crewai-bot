"""
Blog Research Routes
===================

FastAPI routes for blog discovery and research operations.
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..models import (
    BlogResearchRequest,
    BlogResearchResponse,
    BaseResponse,
    PaginationParams
)
from ..auth import get_current_user, get_current_user_optional

# Initialize logger first
logger = logging.getLogger(__name__)

# Import existing agents with proper error handling
try:
    import sys
    import os
    # Add src to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, '..', '..', '..')
    sys.path.append(src_dir)
    
    from seo_automation.agents.enhanced_blog_researcher import EnhancedBlogResearcherAgent
    logger.info("✅ Successfully imported EnhancedBlogResearcherAgent")
except ImportError as e:
    logger.warning(f"⚠️ Could not import real blog researcher agent: {e}. Using mock implementation.")
    EnhancedBlogResearcherAgent = None
except Exception as e:
    logger.error(f"❌ Unexpected error importing agent: {e}. Using mock implementation.")
    EnhancedBlogResearcherAgent = None

router = APIRouter()

# ============================================================================
# Health Check (placed first to avoid routing conflicts)
# ============================================================================

@router.get("/health")
async def blogs_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for blog research system.
    
    Returns:
        dict: Blog research system health status
    """
    return {
        "status": "healthy",
        "service": "Blog Research System",
        "features": [
            "Keyword-based Blog Discovery",
            "Quality Score Assessment",
            "SEO Analysis Integration",
            "Content Analysis",
            "Comment Opportunity Detection",
            "Domain Authority Evaluation"
        ],
        "endpoints": {
            "research": "POST /api/blogs/research",
            "list": "GET /api/blogs/",
            "details": "GET /api/blogs/{id}",
            "analyze": "POST /api/blogs/{id}/analyze",
            "analysis": "GET /api/blogs/{id}/analysis",
            "analytics": "GET /api/blogs/analytics/overview"
        }
    }

# ============================================================================
# Blog Research Operations
# ============================================================================

@router.post("/research", response_model=BlogResearchResponse)
async def research_blogs(
    request: BlogResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BlogResearchResponse:
    """
    Research and discover blogs using real EnhancedBlogResearcherAgent.
    
    Args:
        request: Blog research parameters
        current_user: Authenticated user
        
    Returns:
        BlogResearchResponse: Discovered blogs with metadata
    """
    logger.info(f"🚀 Starting real blog research for keywords: {request.keywords}")
    
    try:
        if EnhancedBlogResearcherAgent is None:
            logger.warning("⚠️ EnhancedBlogResearcherAgent not available, using mock data")
            # Fallback to mock data if agent not available
            mock_blogs = [
                {
                    "url": "https://searchengineland.com/category/seo",
                    "title": "Search Engine Land - SEO News (Mock)",
                    "description": "Latest SEO news, tips and strategies for search engine optimization",
                    "domain": "searchengineland.com",
                    "authority_score": 0.94,
                    "quality_score": 0.91,
                    "comment_opportunity": True,
                    "seo_metrics": {
                        "domain_authority": 89,
                        "page_authority": 76,
                        "traffic_estimate": 2500000,
                        "backlinks": 450000
                    },
                    "discovered_at": datetime.utcnow()
                }
            ]
            
            return BlogResearchResponse(
                blogs=mock_blogs,
                total_discovered=len(mock_blogs),
                quality_filtered=len(mock_blogs),
                keywords_used=request.keywords,
                execution_time=2.1,
                cost=0.15,
                message="Blog research completed (mock data - agent not available)"
            )
        
        # Use the real EnhancedBlogResearcherAgent
        logger.info(f"📋 Using real EnhancedBlogResearcherAgent for research...")
        
        # Create agent instance
        blog_researcher = EnhancedBlogResearcherAgent()
        
        # Prepare research parameters
        research_params = {
            "keywords": request.keywords,
            "max_blogs": request.max_results,
            "quality_threshold": request.quality_threshold,
            "target_domains": request.target_domains or [],
            "exclude_domains": request.exclude_domains or []
        }
        
        # Execute blog research using real agent
        start_time = datetime.utcnow()
        research_result = blog_researcher.research_blogs(research_params)
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ Real blog research completed in {execution_time:.2f} seconds")
        
        # Convert agent results to API response format
        discovered_blogs = []
        if research_result and 'blogs' in research_result:
            for blog in research_result['blogs']:
                discovered_blogs.append({
                    "url": blog.get('url', ''),
                    "title": blog.get('title', ''),
                    "description": blog.get('description', ''),
                    "domain": blog.get('domain', ''),
                    "authority_score": blog.get('authority_score', 0.0),
                    "quality_score": blog.get('quality_score', 0.0),
                    "comment_opportunity": blog.get('comment_opportunity', False),
                    "seo_metrics": blog.get('seo_metrics', {}),
                    "discovered_at": datetime.utcnow()
                })
        
        return BlogResearchResponse(
            blogs=discovered_blogs,
            total_discovered=research_result.get('total_discovered', len(discovered_blogs)),
            quality_filtered=len(discovered_blogs),
            keywords_used=request.keywords,
            execution_time=execution_time,
            cost=research_result.get('cost', 0.0),
            message="Blog research completed successfully using real agent"
        )
        
    except Exception as e:
        logger.error(f"❌ Real blog research error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to research blogs: {str(e)}"
        )

@router.get("/", response_model=BaseResponse)
async def list_discovered_blogs(
    pagination: PaginationParams = Depends(),
    domain_filter: Optional[str] = None,
    min_quality: Optional[float] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    List previously discovered blogs with filtering and pagination.
    
    Args:
        pagination: Pagination parameters
        domain_filter: Optional domain filter
        min_quality: Minimum quality score filter
        current_user: Authenticated user
        
    Returns:
        BaseResponse: List of discovered blogs
    """
    logger.info(f"Listing discovered blogs for user: {current_user['username']}")
    
    try:
        # Mock discovered blogs data
        all_blogs = [
            {
                "id": "blog-1",
                "url": "https://searchengineland.com/category/seo",
                "title": "Search Engine Land - SEO News",
                "domain": "searchengineland.com",
                "quality_score": 0.91,
                "authority_score": 0.94,
                "discovered_at": datetime.utcnow().isoformat(),
                "campaign_id": "campaign-1",
                "status": "analyzed"
            },
            {
                "id": "blog-2",
                "url": "https://moz.com/blog",
                "title": "Moz Blog - SEO and Inbound Marketing",
                "domain": "moz.com",
                "quality_score": 0.89,
                "authority_score": 0.92,
                "discovered_at": datetime.utcnow().isoformat(),
                "campaign_id": "campaign-1",
                "status": "analyzed"
            },
            {
                "id": "blog-3",
                "url": "https://backlinko.com/blog",
                "title": "Backlinko - SEO Training",
                "domain": "backlinko.com",
                "quality_score": 0.85,
                "authority_score": 0.88,
                "discovered_at": datetime.utcnow().isoformat(),
                "campaign_id": "campaign-2",
                "status": "pending"
            }
        ]
        
        # Apply filters
        filtered_blogs = all_blogs
        
        if domain_filter:
            filtered_blogs = [
                blog for blog in filtered_blogs 
                if domain_filter.lower() in blog["domain"].lower()
            ]
        
        if min_quality:
            filtered_blogs = [
                blog for blog in filtered_blogs 
                if blog["quality_score"] >= min_quality
            ]
        
        # Apply pagination
        start_idx = (pagination.page - 1) * pagination.page_size
        end_idx = start_idx + pagination.page_size
        paginated_blogs = filtered_blogs[start_idx:end_idx]
        
        return BaseResponse(
            message="Discovered blogs retrieved successfully",
            **{
                "blogs": paginated_blogs,
                "total": len(filtered_blogs),
                "page": pagination.page,
                "page_size": pagination.page_size
            }
        )
        
    except Exception as e:
        logger.error(f"Blog listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blogs: {str(e)}"
        )

@router.get("/{blog_id}", response_model=BaseResponse)
async def get_blog_details(
    blog_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get detailed information about a specific blog.
    
    Args:
        blog_id: Blog identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Detailed blog information
    """
    logger.info(f"Getting blog details for: {blog_id}")
    
    try:
        # Mock blog details
        if blog_id == "blog-1":
            blog_details = {
                "id": "blog-1",
                "url": "https://searchengineland.com/category/seo",
                "title": "Search Engine Land - SEO News",
                "description": "Latest SEO news, tips and strategies for search engine optimization",
                "domain": "searchengineland.com",
                "quality_score": 0.91,
                "authority_score": 0.94,
                "comment_opportunity": True,
                "discovered_at": datetime.utcnow().isoformat(),
                "analyzed_at": datetime.utcnow().isoformat(),
                "campaign_id": "campaign-1",
                "status": "analyzed",
                "seo_metrics": {
                    "domain_authority": 89,
                    "page_authority": 76,
                    "traffic_estimate": 2500000,
                    "backlinks": 450000,
                    "organic_keywords": 125000
                },
                "content_analysis": {
                    "content_type": "News & Updates",
                    "posting_frequency": "Daily",
                    "average_word_count": 850,
                    "engagement_metrics": {
                        "average_comments": 45,
                        "social_shares": 230,
                        "time_on_page": 185
                    }
                },
                "comment_analysis": {
                    "comments_enabled": True,
                    "moderation_level": "Medium",
                    "response_rate": 0.78,
                    "spam_filtering": True
                }
            }
            
            return BaseResponse(
                message="Blog details retrieved successfully",
                **{"blog": blog_details}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Blog details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog details: {str(e)}"
        )

# ============================================================================
# Blog Analysis Operations
# ============================================================================

@router.post("/{blog_id}/analyze", response_model=BaseResponse)
async def analyze_blog(
    blog_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Perform detailed analysis of a specific blog.
    
    Args:
        blog_id: Blog identifier
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Analysis initiation confirmation
    """
    logger.info(f"Starting blog analysis for: {blog_id}")
    
    try:
        # Add background task for blog analysis
        background_tasks.add_task(analyze_blog_background, blog_id)
        
        return BaseResponse(
            message=f"Blog analysis started for {blog_id}. Processing in background."
        )
        
    except Exception as e:
        logger.error(f"Blog analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start blog analysis: {str(e)}"
        )

@router.get("/{blog_id}/analysis", response_model=BaseResponse)
async def get_blog_analysis(
    blog_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get analysis results for a specific blog.
    
    Args:
        blog_id: Blog identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Blog analysis results
    """
    logger.info(f"Getting blog analysis for: {blog_id}")
    
    try:
        # Mock analysis results
        analysis = {
            "blog_id": blog_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "status": "completed",
            "seo_analysis": {
                "title_optimization": 0.85,
                "content_quality": 0.90,
                "keyword_density": 0.78,
                "readability_score": 0.82,
                "technical_seo": 0.88
            },
            "content_analysis": {
                "topics": ["SEO", "Digital Marketing", "Search Algorithms"],
                "sentiment": "Neutral",
                "expertise_level": "Advanced",
                "target_audience": "SEO Professionals"
            },
            "engagement_potential": {
                "comment_likelihood": 0.85,
                "social_share_potential": 0.78,
                "backlink_opportunities": 0.82
            },
            "recommendations": [
                "Focus on technical SEO topics for better engagement",
                "Comments should be expert-level insights",
                "Best posting times: 9-11 AM EST, Tuesday-Thursday"
            ]
        }
        
        return BaseResponse(
            message="Blog analysis retrieved successfully",
            **{"analysis": analysis}
        )
        
    except Exception as e:
        logger.error(f"Blog analysis retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog analysis: {str(e)}"
        )

# ============================================================================
# Blog Statistics and Analytics
# ============================================================================

@router.get("/analytics/overview", response_model=BaseResponse)
async def get_blogs_analytics(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get overview analytics for blog research activities.
    
    Args:
        days: Number of days to include in analytics
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Blog research analytics
    """
    logger.info(f"Getting blog analytics for {days} days")
    
    try:
        # Mock analytics data
        analytics = {
            "period": f"Last {days} days",
            "summary": {
                "total_blogs_discovered": 1247,
                "unique_domains": 456,
                "average_quality_score": 0.78,
                "comment_opportunities": 892,
                "analysis_completed": 1156
            },
            "quality_distribution": {
                "excellent": 245,
                "good": 567,
                "average": 321,
                "poor": 114
            },
            "domain_authority_breakdown": {
                "90-100": 89,
                "80-89": 234,
                "70-79": 445,
                "60-69": 301,
                "below_60": 178
            },
            "top_domains": [
                {"domain": "searchengineland.com", "count": 45, "avg_quality": 0.91},
                {"domain": "moz.com", "count": 38, "avg_quality": 0.89},
                {"domain": "backlinko.com", "count": 32, "avg_quality": 0.85},
                {"domain": "semrush.com", "count": 29, "avg_quality": 0.87},
                {"domain": "ahrefs.com", "count": 27, "avg_quality": 0.88}
            ],
            "trending_topics": [
                {"topic": "AI in SEO", "count": 156},
                {"topic": "Core Web Vitals", "count": 134},
                {"topic": "Local SEO", "count": 123},
                {"topic": "E-A-T Guidelines", "count": 109},
                {"topic": "Voice Search", "count": 98}
            ]
        }
        
        return BaseResponse(
            message="Blog analytics retrieved successfully",
            **{"analytics": analytics}
        )
        
    except Exception as e:
        logger.error(f"Blog analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog analytics: {str(e)}"
        )

# ============================================================================
# Background Tasks
# ============================================================================

async def analyze_blog_background(blog_id: str):
    """
    Background task for blog analysis.
    
    Args:
        blog_id: Blog identifier
    """
    logger.info(f"Background blog analysis started for: {blog_id}")
    
    try:
        # Simulate blog analysis processing
        import asyncio
        await asyncio.sleep(5)  # Simulate processing time
        
        logger.info(f"Background blog analysis completed for: {blog_id}")
        
    except Exception as e:
        logger.error(f"Background blog analysis error for {blog_id}: {e}")

