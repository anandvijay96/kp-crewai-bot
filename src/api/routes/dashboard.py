"""
Dashboard Data Route
====================

Provides aggregated data for the Dashboard.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
# Import get_current_user with fallback
try:
    from ..auth import get_current_user
except ImportError:
    def get_current_user():
        return {"username": "test_user", "email": "test@example.com"}
# from ..services.campaign_service import CampaignService
# from ..services.blog_research_service import BlogResearchService
# from ..services.comment_service import CommentService

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)

@router.get("/data")
async def get_dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Fetches summarized data for the dashboard view.

    Args:
        current_user: Dict containing the authenticated user's details

    Returns:
        Dashboard data containing key metrics
    """
    logger.info(f"Fetching dashboard data for user: {current_user['email']}")

    try:
        # Return mock dashboard data for MVP
        return {
            "activeCampaigns": 3,
            "blogsDiscovered": 247,
            "commentsGenerated": 156,
            "successRate": 87.5,
            "recentCampaigns": [
                {
                    "id": "campaign-1",
                    "name": "SEO Tools Campaign",
                    "status": "active",
                    "progress": 68
                },
                {
                    "id": "campaign-2", 
                    "name": "Digital Marketing Blog Outreach",
                    "status": "active",
                    "progress": 42
                },
                {
                    "id": "campaign-3",
                    "name": "E-commerce SEO Comments", 
                    "status": "paused",
                    "progress": 23
                }
            ],
            "topBlogs": [
                {
                    "domain": "searchengineland.com",
                    "comments": 23,
                    "quality": 0.91
                },
                {
                    "domain": "moz.com", 
                    "comments": 18,
                    "quality": 0.89
                },
                {
                    "domain": "backlinko.com",
                    "comments": 15,
                    "quality": 0.85
                },
                {
                    "domain": "semrush.com",
                    "comments": 12,
                    "quality": 0.87
                }
            ]
        }

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

