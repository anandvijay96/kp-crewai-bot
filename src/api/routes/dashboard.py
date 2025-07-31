"""
Dashboard Data Route
====================

Provides aggregated data for the Dashboard.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from ..services.integration_service import BunIntegrationService

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
        # Initialize Bun integration service
        bun_service = BunIntegrationService()
        
        # Fetch real-time data
        scraping_stats = await bun_service.scrape_url("https://example.com")
        
        # Return transformed data
        return {
            "activeCampaigns": None,
            "blogsDiscovered": len(scraping_stats.get('data', {}).get('links', [])),
            "commentsGenerated": len(scraping_stats.get('data', {}).get('comments', [])),
            "successRate": 100,  # Real success metrics to be calculated
            "recentCampaigns": scraping_stats.get('data', {}).get('recentCampaigns', []),
            "topBlogs": scraping_stats.get('data', {}).get('topBlogs', []),
        }

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

