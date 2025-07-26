"""
Campaign Service
================

Service layer for campaign management with database integration.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.campaign import Campaign, CampaignStatus, CampaignTask
from ..models.user import User
from ...seo_automation.utils.database import db_manager

logger = logging.getLogger(__name__)

class CampaignService:
    """Service for managing SEO campaigns."""
    
    @staticmethod
    def create_campaign(campaign_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Create a new campaign.
        
        Args:
            campaign_data: Campaign configuration data
            user_id: ID of the user creating the campaign
            
        Returns:
            Dict containing created campaign data
        """
        try:
            with db_manager.get_session() as session:
                # Create campaign record
                campaign = Campaign(
                    id=str(uuid.uuid4()),
                    name=campaign_data["name"],
                    description=campaign_data.get("description", ""),
                    keywords=campaign_data.get("keywords", []),
                    target_blogs=campaign_data.get("target_blogs", []),
                    comment_styles=campaign_data.get("comment_styles", []),
                    max_blogs=campaign_data.get("max_blogs", 10),
                    max_comments_per_blog=campaign_data.get("max_comments_per_blog", 3),
                    quality_threshold=campaign_data.get("quality_threshold", 0.7),
                    budget_limit=campaign_data.get("budget_limit"),
                    status=CampaignStatus.CREATED,
                    created_by_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(campaign)
                session.commit()
                session.refresh(campaign)
                
                logger.info(f"Campaign created successfully: {campaign.id}")
                
                return CampaignService._campaign_to_dict(campaign)
                
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            raise

    @staticmethod
    def get_campaign(campaign_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get campaign by ID.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            Campaign data or None if not found
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return None
                
                return CampaignService._campaign_to_dict(campaign, include_tasks=True)
                
        except Exception as e:
            logger.error(f"Failed to get campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def list_campaigns(
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status_filter: Optional[CampaignStatus] = None
    ) -> Dict[str, Any]:
        """
        List campaigns for a user with pagination.
        
        Args:
            user_id: User ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            
        Returns:
            Dict containing campaigns list and pagination info
        """
        try:
            with db_manager.get_session() as session:
                query = session.query(Campaign).filter(Campaign.created_by_id == user_id)
                
                if status_filter:
                    query = query.filter(Campaign.status == status_filter)
                
                # Get total count
                total = query.count()
                
                # Apply pagination
                campaigns = query.order_by(Campaign.created_at.desc()).offset(
                    (page - 1) * page_size
                ).limit(page_size).all()
                
                campaign_list = [
                    CampaignService._campaign_to_dict(campaign) 
                    for campaign in campaigns
                ]
                
                return {
                    "campaigns": campaign_list,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "pages": (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            logger.error(f"Failed to list campaigns for user {user_id}: {e}")
            raise

    @staticmethod
    def update_campaign(
        campaign_id: str,
        update_data: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Update campaign configuration.
        
        Args:
            campaign_id: Campaign identifier
            update_data: Fields to update
            user_id: User ID for ownership check
            
        Returns:
            Updated campaign data or None if not found
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return None
                
                # Update allowed fields
                updateable_fields = [
                    "name", "description", "quality_threshold", 
                    "budget_limit", "status"
                ]
                
                for field in updateable_fields:
                    if field in update_data:
                        setattr(campaign, field, update_data[field])
                
                campaign.updated_at = datetime.utcnow()
                
                session.commit()
                session.refresh(campaign)
                
                logger.info(f"Campaign updated successfully: {campaign_id}")
                
                return CampaignService._campaign_to_dict(campaign)
                
        except Exception as e:
            logger.error(f"Failed to update campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def delete_campaign(campaign_id: str, user_id: int) -> bool:
        """
        Delete a campaign.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return False
                
                # Delete associated tasks first
                session.query(CampaignTask).filter(
                    CampaignTask.campaign_id == campaign_id
                ).delete()
                
                # Delete campaign
                session.delete(campaign)
                session.commit()
                
                logger.info(f"Campaign deleted successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def start_campaign(campaign_id: str, user_id: int) -> bool:
        """
        Start campaign execution.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            True if started, False if not found or invalid state
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return False
                
                # Check if campaign can be started
                if campaign.status not in [CampaignStatus.CREATED, CampaignStatus.PAUSED]:
                    logger.warning(f"Campaign {campaign_id} cannot be started from status: {campaign.status}")
                    return False
                
                # Update status
                campaign.status = CampaignStatus.RUNNING
                campaign.started_at = datetime.utcnow()
                campaign.updated_at = datetime.utcnow()
                
                session.commit()
                
                logger.info(f"Campaign started successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def pause_campaign(campaign_id: str, user_id: int) -> bool:
        """
        Pause campaign execution.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            True if paused, False if not found or invalid state
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return False
                
                # Check if campaign can be paused
                if campaign.status != CampaignStatus.RUNNING:
                    logger.warning(f"Campaign {campaign_id} cannot be paused from status: {campaign.status}")
                    return False
                
                # Update status
                campaign.status = CampaignStatus.PAUSED
                campaign.updated_at = datetime.utcnow()
                
                session.commit()
                
                logger.info(f"Campaign paused successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to pause campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def stop_campaign(campaign_id: str, user_id: int) -> bool:
        """
        Stop campaign execution.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            True if stopped, False if not found
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return False
                
                # Update status
                campaign.status = CampaignStatus.STOPPED
                campaign.ended_at = datetime.utcnow()
                campaign.updated_at = datetime.utcnow()
                
                session.commit()
                
                logger.info(f"Campaign stopped successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def get_campaign_analytics(campaign_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get campaign analytics and performance metrics.
        
        Args:
            campaign_id: Campaign identifier
            user_id: User ID for ownership check
            
        Returns:
            Campaign analytics data or None if not found
        """
        try:
            with db_manager.get_session() as session:
                campaign = session.query(Campaign).filter(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.created_by_id == user_id
                    )
                ).first()
                
                if not campaign:
                    return None
                
                # Get campaign tasks
                tasks = session.query(CampaignTask).filter(
                    CampaignTask.campaign_id == campaign_id
                ).all()
                
                # Calculate analytics
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.status == "completed"])
                failed_tasks = len([t for t in tasks if t.status == "failed"])
                
                progress = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0
                success_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0
                
                # Calculate execution time
                execution_time = 0
                if campaign.started_at:
                    end_time = campaign.ended_at or datetime.utcnow()
                    execution_time = (end_time - campaign.started_at).total_seconds()
                
                analytics = {
                    "campaign_id": campaign.id,
                    "status": campaign.status.value,
                    "progress": progress,
                    "success_rate": success_rate,
                    "execution_time": execution_time,
                    "task_summary": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "failed_tasks": failed_tasks,
                        "pending_tasks": total_tasks - completed_tasks - failed_tasks
                    },
                    "performance_metrics": {
                        "blogs_discovered": sum(getattr(t, 'blogs_discovered', 0) for t in tasks),
                        "comments_generated": sum(getattr(t, 'comments_generated', 0) for t in tasks),
                        "quality_score": campaign.quality_threshold,
                        "budget_used": sum(getattr(t, 'cost', 0) for t in tasks),
                        "budget_remaining": max(0, (campaign.budget_limit or 0) - sum(getattr(t, 'cost', 0) for t in tasks))
                    },
                    "timeline": {
                        "created_at": campaign.created_at.isoformat(),
                        "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
                        "ended_at": campaign.ended_at.isoformat() if campaign.ended_at else None,
                        "last_updated": campaign.updated_at.isoformat()
                    }
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get analytics for campaign {campaign_id}: {e}")
            raise

    @staticmethod
    def _campaign_to_dict(campaign: Campaign, include_tasks: bool = False) -> Dict[str, Any]:
        """
        Convert Campaign model to dictionary.
        
        Args:
            campaign: Campaign model instance
            include_tasks: Whether to include task details
            
        Returns:
            Campaign data as dictionary
        """
        data = {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "status": campaign.status.value,
            "keywords": campaign.keywords,
            "target_blogs": campaign.target_blogs,
            "comment_styles": campaign.comment_styles,
            "max_blogs": campaign.max_blogs,
            "max_comments_per_blog": campaign.max_comments_per_blog,
            "quality_threshold": campaign.quality_threshold,
            "budget_limit": campaign.budget_limit,
            "created_by_id": campaign.created_by_id,
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat(),
            "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
            "ended_at": campaign.ended_at.isoformat() if campaign.ended_at else None,
            "estimated_cost": getattr(campaign, 'estimated_cost', 0.0),
            "actual_cost": getattr(campaign, 'actual_cost', 0.0),
            "progress": getattr(campaign, 'progress', 0.0)
        }
        
        if include_tasks:
            # Add task information (would need to query separately)
            data["tasks"] = []
        
        return data
