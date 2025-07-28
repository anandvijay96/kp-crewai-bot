"""
Dashboard Data Route
====================

Provides aggregated data for the Dashboard.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

# Note: get_current_user will be provided by the test server
# from .auth import get_current_user
# from ..services.campaign_service import CampaignService
# from ..services.blog_research_service import BlogResearchService
# from ..services.comment_service import CommentService

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)

@router.get("/dashboard/data")
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
        # For now, return mock data (replace with real data later)
        # TODO: Implement actual database queries when services are ready
        return {
            "activeCampaigns": 12,
            "blogsDiscovered": 2847,
            "commentsGenerated": 1234,
            "successRate": 87.5,
            "recentCampaigns": [
                {"name": "SEO Campaign - Digital Marketing", "status": "Active", "blogs": 245},
                {"name": "Content Marketing Outreach", "status": "Active", "blogs": 189},
                {"name": "Tech Blog Analysis Q1", "status": "Paused", "blogs": 156}
            ],
            "topBlogs": [
                {"title": "Advanced SEO Strategies for 2024", "domain": "searchengineland.com", "score": 95, "comments": 3},
                {"title": "Building Scalable SaaS Products", "domain": "medium.com", "score": 92, "comments": 2},
                {"title": "Machine Learning Best Practices", "domain": "towardsdatascience.com", "score": 89, "comments": 1}
            ]
        }

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

