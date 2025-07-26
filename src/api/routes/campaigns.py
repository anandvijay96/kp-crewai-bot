"""
Campaign Management Routes
==========================

FastAPI routes for campaign creation, management, and monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import uuid
import asyncio
from datetime import datetime

from ..models import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    PaginationParams,
    BaseResponse,
    CampaignStatus
)
from ..auth import get_current_user

# Setup logger first
logger = logging.getLogger(__name__)

# Import existing agents and database with proper error handling
try:
    # Import the real agents using relative imports
    from ...seo_automation.agents.campaign_manager import CampaignManagerAgent
    from ...seo_automation.utils.database import DatabaseManager
    logger.info("✅ Successfully imported real agents and database models")
    AGENTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Could not import real agents: {e}. Using mock implementation.")
    CampaignManagerAgent = None
    DatabaseManager = None
    AGENTS_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Unexpected error importing agents: {e}. Using mock implementation.")
    CampaignManagerAgent = None
    DatabaseManager = None
    AGENTS_AVAILABLE = False

router = APIRouter()

# Global campaign manager instance
campaign_manager = None

def get_campaign_manager():
    """Get or create campaign manager instance."""
    global campaign_manager
    if campaign_manager is None and AGENTS_AVAILABLE:
        try:
            campaign_manager = CampaignManagerAgent()
            logger.info("✅ Real CampaignManagerAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize CampaignManagerAgent: {e}")
            campaign_manager = None
    return campaign_manager

# ============================================================================
# Campaign CRUD Operations
# ============================================================================

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignResponse:
    """
    Create a new SEO campaign.
    
    Args:
        campaign_data: Campaign configuration data
        current_user: Authenticated user
        
    Returns:
        CampaignResponse: Created campaign details
        
    Raises:
        HTTPException: If campaign creation fails
    """
    logger.info(f"Creating campaign '{campaign_data.name}' for user: {current_user['username']}")
    
    try:
        # Prepare campaign configuration
        config = {
            "campaign_id": str(uuid.uuid4()),
            "name": campaign_data.name,
            "description": campaign_data.description,
            "keywords": campaign_data.keywords,
            "target_blogs": campaign_data.target_blogs or [],
            "comment_styles": [style.value for style in campaign_data.comment_styles],
            "max_blogs": campaign_data.max_blogs,
            "max_comments_per_blog": campaign_data.max_comments_per_blog,
            "quality_threshold": campaign_data.quality_threshold,
            "budget_limit": campaign_data.budget_limit,
            "created_by": current_user["username"],
            "created_at": datetime.utcnow()
        }
        
        # Try to use real agent first, fallback to mock
        manager = get_campaign_manager()
        if manager is not None:
            logger.info("🤖 Using real CampaignManagerAgent for campaign creation")
            campaign = manager.create_campaign(config)
        else:
            logger.info("📋 Using mock campaign creation (agent not available)")
            # Mock campaign creation when real agent is not available
            campaign = {
                "campaign_id": config["campaign_id"],
                "name": config["name"],
                "description": config["description"],
                "status": "created",
                "keywords": config["keywords"],
                "target_blogs": config["target_blogs"],
                "comment_styles": config["comment_styles"],
                "max_blogs": config["max_blogs"],
                "max_comments_per_blog": config["max_comments_per_blog"],
                "quality_threshold": config["quality_threshold"],
                "budget_limit": config["budget_limit"],
                "created_by": config["created_by"],
                "created_at": config["created_at"],
                "updated_at": config["created_at"],
                "tasks": [],
                "estimated_cost": 0.0,
                "estimated_duration": 0,
                "progress": 0.0
            }
        
        # Convert campaign data for API response
        campaign_response = {
            "id": campaign.get("campaign_id"),
            "name": campaign.get("name"),
            "description": campaign.get("description"),
            "status": campaign.get("status", "created"),
            "keywords": campaign.get("keywords", []),
            "target_blogs": campaign.get("target_blogs", []),
            "comment_styles": campaign.get("comment_styles", []),
            "max_blogs": campaign.get("max_blogs", 10),
            "max_comments_per_blog": campaign.get("max_comments_per_blog", 3),
            "quality_threshold": campaign.get("quality_threshold", 0.7),
            "budget_limit": campaign.get("budget_limit"),
            "created_by": campaign.get("created_by"),
            "created_at": campaign.get("created_at", datetime.utcnow()).isoformat(),
            "updated_at": campaign.get("updated_at", datetime.utcnow()).isoformat(),
            "tasks": campaign.get("tasks", []),
            "estimated_cost": campaign.get("estimated_cost", 0.0),
            "estimated_duration": campaign.get("estimated_duration", 0),
            "progress": campaign.get("progress", 0.0)
        }
        
        logger.info(f"Campaign created successfully: {campaign_response['id']}")
        
        return CampaignResponse(
            campaign=campaign_response,
            message="Campaign created successfully"
        )
        
    except Exception as e:
        logger.error(f"Campaign creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/", response_model=CampaignListResponse)
async def list_campaigns(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[CampaignStatus] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignListResponse:
    """
    List campaigns with pagination and filtering.
    
    Args:
        pagination: Pagination parameters
        status_filter: Optional status filter
        current_user: Authenticated user
        
    Returns:
        CampaignListResponse: List of campaigns with pagination info
    """
    logger.info(f"Listing campaigns for user: {current_user['username']}")
    
    try:
        # For MVP, return mock data structure
        # In production, this would query the database
        campaigns = []
        
        # Mock campaign data for demonstration
        mock_campaigns = [
            {
                "id": "campaign-1",
                "name": "SEO Campaign 1",
                "description": "Test campaign for blog commenting",
                "status": "completed",
                "keywords": ["SEO", "digital marketing"],
                "created_by": current_user["username"],
                "created_at": datetime.utcnow().isoformat(),
                "progress": 1.0,
                "estimated_cost": 15.50,
                "results_summary": {
                    "blogs_discovered": 25,
                    "comments_generated": 75,
                    "quality_score": 0.85
                }
            },
            {
                "id": "campaign-2", 
                "name": "Content Marketing Campaign",
                "description": "Automated commenting for content marketing",
                "status": "running",
                "keywords": ["content marketing", "automation"],
                "created_by": current_user["username"],
                "created_at": datetime.utcnow().isoformat(),
                "progress": 0.65,
                "estimated_cost": 22.30,
                "results_summary": {
                    "blogs_discovered": 18,
                    "comments_generated": 35,
                    "quality_score": 0.78
                }
            }
        ]
        
        # Apply status filter if provided
        if status_filter:
            campaigns = [c for c in mock_campaigns if c["status"] == status_filter.value]
        else:
            campaigns = mock_campaigns
        
        # Apply pagination
        start_idx = (pagination.page - 1) * pagination.page_size
        end_idx = start_idx + pagination.page_size
        paginated_campaigns = campaigns[start_idx:end_idx]
        
        total = len(campaigns)
        
        logger.info(f"Retrieved {len(paginated_campaigns)} campaigns (total: {total})")
        
        return CampaignListResponse(
            campaigns=paginated_campaigns,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            message="Campaigns retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Campaign listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaigns: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignResponse:
    """
    Get campaign details by ID.
    
    Args:
        campaign_id: Campaign identifier
        current_user: Authenticated user
        
    Returns:
        CampaignResponse: Campaign details
        
    Raises:
        HTTPException: If campaign not found
    """
    logger.info(f"Retrieving campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, return mock campaign data
        # In production, this would query the database
        if campaign_id == "campaign-1":
            campaign = {
                "id": "campaign-1",
                "name": "SEO Campaign 1",
                "description": "Test campaign for blog commenting",
                "status": "completed",
                "keywords": ["SEO", "digital marketing"],
                "target_blogs": [],
                "comment_styles": ["engaging", "question"],
                "max_blogs": 10,
                "max_comments_per_blog": 3,
                "quality_threshold": 0.7,
                "budget_limit": 50.0,
                "created_by": current_user["username"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "progress": 1.0,
                "estimated_cost": 15.50,
                "actual_cost": 14.25,
                "tasks": [
                    {
                        "id": "task-1",
                        "name": "Blog Discovery",
                        "status": "completed",
                        "progress": 1.0
                    },
                    {
                        "id": "task-2", 
                        "name": "Comment Generation",
                        "status": "completed",
                        "progress": 1.0
                    }
                ],
                "results": {
                    "blogs_discovered": 25,
                    "comments_generated": 75,
                    "quality_score": 0.85,
                    "execution_time": 245.6
                }
            }
            
            return CampaignResponse(
                campaign=campaign,
                message="Campaign retrieved successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign: {str(e)}"
        )

@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignResponse:
    """
    Update campaign configuration.
    
    Args:
        campaign_id: Campaign identifier
        campaign_update: Campaign update data
        current_user: Authenticated user
        
    Returns:
        CampaignResponse: Updated campaign details
        
    Raises:
        HTTPException: If campaign not found or update fails
    """
    logger.info(f"Updating campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, simulate campaign update
        # In production, this would update the database
        
        # Validate campaign exists
        if campaign_id not in ["campaign-1", "campaign-2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Create updated campaign response
        updated_campaign = {
            "id": campaign_id,
            "name": campaign_update.name or "Updated Campaign Name",
            "description": campaign_update.description or "Updated description",
            "status": campaign_update.status.value if campaign_update.status else "created",
            "quality_threshold": campaign_update.quality_threshold or 0.7,
            "budget_limit": campaign_update.budget_limit or 50.0,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": current_user["username"]
        }
        
        logger.info(f"Campaign updated successfully: {campaign_id}")
        
        return CampaignResponse(
            campaign=updated_campaign,
            message="Campaign updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}", response_model=BaseResponse)
async def delete_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Delete a campaign.
    
    Args:
        campaign_id: Campaign identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Deletion confirmation
        
    Raises:
        HTTPException: If campaign not found or deletion fails
    """
    logger.info(f"Deleting campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, simulate campaign deletion
        # In production, this would delete from database
        
        if campaign_id not in ["campaign-1", "campaign-2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        logger.info(f"Campaign deleted successfully: {campaign_id}")
        
        return BaseResponse(
            message=f"Campaign {campaign_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

# ============================================================================
# Campaign Execution
# ============================================================================

@router.post("/{campaign_id}/start", response_model=BaseResponse)
async def start_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Start campaign execution.
    
    Args:
        campaign_id: Campaign identifier
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Campaign start confirmation
        
    Raises:
        HTTPException: If campaign not found or start fails
    """
    logger.info(f"Starting campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, simulate campaign start
        # In production, this would start the actual campaign execution
        
        if campaign_id not in ["campaign-1", "campaign-2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Add background task for campaign execution
        background_tasks.add_task(execute_campaign_background, campaign_id)
        
        logger.info(f"Campaign started successfully: {campaign_id}")
        
        return BaseResponse(
            message=f"Campaign {campaign_id} started successfully. Execution is running in the background."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign start error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start campaign: {str(e)}"
        )

@router.post("/{campaign_id}/pause", response_model=BaseResponse)
async def pause_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Pause campaign execution.
    
    Args:
        campaign_id: Campaign identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Campaign pause confirmation
    """
    logger.info(f"Pausing campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, simulate campaign pause
        # In production, this would pause the actual campaign execution
        
        if campaign_id not in ["campaign-1", "campaign-2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        logger.info(f"Campaign paused successfully: {campaign_id}")
        
        return BaseResponse(
            message=f"Campaign {campaign_id} paused successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign pause error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause campaign: {str(e)}"
        )

@router.post("/{campaign_id}/stop", response_model=BaseResponse)
async def stop_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Stop campaign execution.
    
    Args:
        campaign_id: Campaign identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Campaign stop confirmation
    """
    logger.info(f"Stopping campaign {campaign_id} for user: {current_user['username']}")
    
    try:
        # For MVP, simulate campaign stop
        # In production, this would stop the actual campaign execution
        
        if campaign_id not in ["campaign-1", "campaign-2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        logger.info(f"Campaign stopped successfully: {campaign_id}")
        
        return BaseResponse(
            message=f"Campaign {campaign_id} stopped successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign stop error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop campaign: {str(e)}"
        )

# ============================================================================
# Campaign Analytics
# ============================================================================

@router.get("/{campaign_id}/analytics", response_model=BaseResponse)
async def get_campaign_analytics(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get campaign analytics and performance metrics.
    
    Args:
        campaign_id: Campaign identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Campaign analytics data
    """
    logger.info(f"Retrieving analytics for campaign {campaign_id}")
    
    try:
        # For MVP, return mock analytics data
        analytics = {
            "campaign_id": campaign_id,
            "performance_metrics": {
                "blogs_discovered": 25,
                "blogs_analyzed": 23,
                "comments_generated": 75,
                "quality_scores": {
                    "average": 0.85,
                    "minimum": 0.72,
                    "maximum": 0.96
                },
                "success_rate": 0.92
            },
            "cost_analysis": {
                "estimated_cost": 15.50,
                "actual_cost": 14.25,
                "cost_per_blog": 0.62,
                "cost_per_comment": 0.19
            },
            "time_analysis": {
                "total_execution_time": 245.6,
                "average_time_per_blog": 10.7,
                "average_time_per_comment": 3.3
            },
            "quality_breakdown": {
                "excellent": 45,
                "good": 25,
                "acceptable": 5,
                "rejected": 0
            }
        }
        
        return BaseResponse(
            message="Campaign analytics retrieved successfully",
            **{"analytics": analytics}
        )
        
    except Exception as e:
        logger.error(f"Campaign analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign analytics: {str(e)}"
        )

# ============================================================================
# Background Tasks
# ============================================================================

async def execute_campaign_background(campaign_id: str):
    """
    Background task for real campaign execution using CampaignManagerAgent.
    
    Args:
        campaign_id: Campaign identifier
    """
    logger.info(f"🚀 Real campaign execution started for: {campaign_id}")
    
    try:
        if CampaignManagerAgent is None:
            logger.warning("⚠️ CampaignManagerAgent not available, using simulation")
            await asyncio.sleep(5)  # Simulate processing
            logger.info(f"✅ Simulated execution completed for campaign: {campaign_id}")
            return
        
        # Use the real CampaignManagerAgent
        manager = get_campaign_manager()
        
        # Execute the campaign using the real agent
        logger.info(f"📋 Executing campaign {campaign_id} with real CampaignManagerAgent...")
        
        # Mock campaign config for execution (in real implementation, this would come from database)
        campaign_config = {
            "campaign_id": campaign_id,
            "keywords": ["SEO", "digital marketing"],
            "max_blogs": 5,  # Smaller number for testing
            "max_comments_per_blog": 2,
            "quality_threshold": 0.7
        }
        
        # Execute the campaign using the real agent
        result = manager.execute_campaign(campaign_config)
        
        logger.info(f"✅ Real campaign execution completed for: {campaign_id}")
        logger.info(f"📊 Results: {result}")
        
        # TODO: Update database with execution results
        # TODO: Send WebSocket notifications about progress
        
    except Exception as e:
        logger.error(f"❌ Real campaign execution error for {campaign_id}: {e}")
        # TODO: Update campaign status to 'failed' in database

# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def campaigns_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for campaign system.
    
    Returns:
        dict: Campaign system health status
    """
    return {
        "status": "healthy",
        "service": "Campaign Management System",
        "features": [
            "Campaign CRUD Operations",
            "Campaign Execution Control",
            "Real-time Progress Monitoring",
            "Performance Analytics",
            "Background Task Processing"
        ],
        "endpoints": {
            "create": "POST /api/campaigns/",
            "list": "GET /api/campaigns/",
            "get": "GET /api/campaigns/{id}",
            "update": "PATCH /api/campaigns/{id}",
            "delete": "DELETE /api/campaigns/{id}",
            "start": "POST /api/campaigns/{id}/start",
            "pause": "POST /api/campaigns/{id}/pause",
            "stop": "POST /api/campaigns/{id}/stop",
            "analytics": "GET /api/campaigns/{id}/analytics"
        }
    }
