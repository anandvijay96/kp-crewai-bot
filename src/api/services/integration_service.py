"""
Integration Service for Real-time Bun Communication
====================================================

Handles communication with Bun scraping microservice for real-time data.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
import uuid

from ..websocket import (
    notify_campaign_update,
    notify_agent_status,
    notify_task_progress,
    notify_system_event,
    websocket_manager
)
from httpx import AsyncClient
import os

logger = logging.getLogger(__name__)

class BunIntegrationService:
    """Service for integrating Python backend with Bun microservice."""

    BUN_URL = os.getenv('BUN_MICROSERVICE_URL', 'http://localhost:3001')

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        async with AsyncClient() as client:
            response = await client.post(f'{self.BUN_URL}/api/scraping/scrape', json={'url': url})
            response.raise_for_status()
            return response.json()

    async def batch_scrape(self, urls: List[str]) -> Dict[str, Any]:
        async with AsyncClient() as client:
            response = await client.post(f'{self.BUN_URL}/api/scraping/batch-scrape', json={'urls': urls})
            response.raise_for_status()
            return response.json()
    def __init__(self):
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        
    # ============================================================================
    # Campaign Integration
    # ============================================================================
    
    async def start_campaign_execution(
        self, 
        campaign_id: str, 
        config: Dict[str, Any], 
        user_id: str
    ) -> str:
        """
        Start campaign execution with real-time updates.
        
        Args:
            campaign_id: Campaign identifier
            config: Campaign configuration
            user_id: User who started the campaign
            
        Returns:
            str: Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        # Store task metadata
        self.active_tasks[task_id] = {
            "campaign_id": campaign_id,
            "type": "campaign_execution",
            "user_id": user_id,
            "config": config,
            "started_at": datetime.utcnow(),
            "status": "starting",
            "progress": 0.0
        }
        
        # Notify campaign start
        await notify_campaign_update(
            campaign_id=campaign_id,
            status="starting",
            progress=0.0,
            message="Campaign execution is starting..."
        )
        
        # Start background execution
        asyncio.create_task(self._execute_campaign_with_updates(task_id, campaign_id, config))
        
        logger.info(f"Started campaign execution: {campaign_id} (Task: {task_id})")
        return task_id
    
    async def _execute_campaign_with_updates(
        self, 
        task_id: str, 
        campaign_id: str, 
        config: Dict[str, Any]
    ):
        """Execute campaign with real-time progress updates."""
        try:
            # Update task status
            self.active_tasks[task_id]["status"] = "running"
            await notify_campaign_update(
                campaign_id=campaign_id,
                status="running",
                progress=0.1,
                message="Initializing campaign execution..."
            )
            
            # Phase 1: Blog Research
            await self._update_progress(task_id, campaign_id, 0.2, "Researching target blogs...")
            blog_results = await self._execute_blog_research(config)
            
            # Phase 2: Blog Analysis
            await self._update_progress(task_id, campaign_id, 0.4, "Analyzing discovered blogs...")
            analysis_results = await self._execute_blog_analysis(blog_results)
            
            # Phase 3: Comment Generation
            await self._update_progress(task_id, campaign_id, 0.6, "Generating comments...")
            comment_results = await self._execute_comment_generation(analysis_results, config)
            
            # Phase 4: Quality Review
            await self._update_progress(task_id, campaign_id, 0.8, "Reviewing comment quality...")
            review_results = await self._execute_quality_review(comment_results)
            
            # Phase 5: Completion
            await self._update_progress(task_id, campaign_id, 1.0, "Campaign completed successfully!")
            
            # Update final status
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["completed_at"] = datetime.utcnow()
            self.active_tasks[task_id]["results"] = {
                "blogs_researched": len(blog_results),
                "comments_generated": len(comment_results),
                "quality_score": review_results.get("average_quality", 0.0)
            }
            
            await notify_campaign_update(
                campaign_id=campaign_id,
                status="completed",
                progress=1.0,
                message=f"Campaign completed! Generated {len(comment_results)} comments."
            )
            
        except Exception as e:
            logger.error(f"Campaign execution error: {e}")
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            
            await notify_campaign_update(
                campaign_id=campaign_id,
                status="failed",
                progress=self.active_tasks[task_id]["progress"],
                message=f"Campaign failed: {str(e)}"
            )
    
    async def _update_progress(self, task_id: str, campaign_id: str, progress: float, message: str):
        """Update task progress and notify clients."""
        self.active_tasks[task_id]["progress"] = progress
        self.active_tasks[task_id]["current_message"] = message
        
        await notify_campaign_update(
            campaign_id=campaign_id,
            status="running",
            progress=progress,
            message=message
        )
        
        await notify_task_progress(
            task_id=task_id,
            task_type="campaign_execution",
            progress=progress,
            status="running"
        )
    
    # ============================================================================
    # Agent Execution Methods (Mock Implementation)
    # ============================================================================
    
    async def _execute_blog_research(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute blog research phase."""
        await asyncio.sleep(2)  # Simulate research time
        
        # Mock blog research results
        blogs = [
            {
                "id": f"blog-{i}",
                "url": f"https://example-blog-{i}.com",
                "title": f"Example Blog {i}",
                "quality_score": 0.8 + (i * 0.02),
                "domain_authority": 75 + i
            }
            for i in range(min(config.get("max_blogs", 5), 10))
        ]
        
        return blogs
    
    async def _execute_blog_analysis(self, blogs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute blog analysis phase."""
        await asyncio.sleep(1.5)  # Simulate analysis time
        
        # Add analysis data to blogs
        for blog in blogs:
            blog["analysis"] = {
                "seo_score": 0.85,
                "content_quality": 0.80,
                "engagement_potential": 0.75,
                "comment_opportunities": True
            }
        
        return blogs
    
    async def _execute_comment_generation(
        self, 
        blogs: List[Dict[str, Any]], 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute comment generation phase."""
        await asyncio.sleep(3)  # Simulate generation time
        
        comments = []
        comments_per_blog = config.get("max_comments_per_blog", 2)
        
        for blog in blogs:
            for i in range(comments_per_blog):
                comment = {
                    "id": str(uuid.uuid4()),
                    "blog_id": blog["id"],
                    "blog_url": blog["url"],
                    "content": f"Great insights on this topic! This analysis really helps understand the nuances of {blog['title']}.",
                    "style": "engaging",
                    "quality_score": 0.82 + (i * 0.03),
                    "generated_at": datetime.utcnow()
                }
                comments.append(comment)
        
        return comments
    
    async def _execute_quality_review(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute quality review phase."""
        await asyncio.sleep(1)  # Simulate review time
        
        total_quality = sum(comment["quality_score"] for comment in comments)
        average_quality = total_quality / len(comments) if comments else 0.0
        
        # Update comments with review status
        for comment in comments:
            comment["review_status"] = "approved" if comment["quality_score"] > 0.7 else "needs_revision"
            comment["reviewed_at"] = datetime.utcnow()
        
        return {
            "total_comments": len(comments),
            "approved_comments": len([c for c in comments if c["review_status"] == "approved"]),
            "average_quality": average_quality,
            "review_completed_at": datetime.utcnow()
        }
    
    # ============================================================================
    # Agent Status Management
    # ============================================================================
    
    async def update_agent_status(
        self, 
        agent_type: str, 
        status: str, 
        metrics: Optional[Dict[str, Any]] = None
    ):
        """Update agent status and notify clients."""
        self.agent_status[agent_type] = {
            "status": status,
            "metrics": metrics or {},
            "last_updated": datetime.utcnow()
        }
        
        await notify_agent_status(
            agent_type=agent_type,
            status=status,
            metrics=metrics or {}
        )
        
        logger.info(f"Updated agent status: {agent_type} -> {status}")
    
    async def get_agent_status(self, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Get current agent status."""
        if agent_type:
            return self.agent_status.get(agent_type, {})
        return self.agent_status
    
    # ============================================================================
    # Task Management
    # ============================================================================
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        return self.active_tasks.get(task_id)
    
    async def list_active_tasks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active tasks, optionally filtered by user."""
        tasks = []
        for task_id, task_data in self.active_tasks.items():
            if user_id is None or task_data.get("user_id") == user_id:
                task_copy = task_data.copy()
                task_copy["task_id"] = task_id
                tasks.append(task_copy)
        
        return tasks
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task."""
        if task_id not in self.active_tasks:
            return False
        
        task_data = self.active_tasks[task_id]
        task_data["status"] = "cancelled"
        task_data["cancelled_at"] = datetime.utcnow()
        
        # Notify cancellation
        if task_data["type"] == "campaign_execution":
            await notify_campaign_update(
                campaign_id=task_data["campaign_id"],
                status="cancelled",
                progress=task_data["progress"],
                message="Campaign execution was cancelled"
            )
        
        await notify_task_progress(
            task_id=task_id,
            task_type=task_data["type"],
            progress=task_data["progress"],
            status="cancelled"
        )
        
        logger.info(f"Cancelled task: {task_id}")
        return True
    
    # ============================================================================
    # System Events
    # ============================================================================
    
    async def notify_system_maintenance(self, message: str, duration_minutes: int = 5):
        """Notify users about system maintenance."""
        await notify_system_event(
            event_type="maintenance",
            message=message,
            data={
                "duration_minutes": duration_minutes,
                "scheduled_at": datetime.utcnow().isoformat()
            }
        )
    
    async def notify_system_update(self, version: str, features: List[str]):
        """Notify users about system updates."""
        await notify_system_event(
            event_type="update",
            message=f"System updated to version {version}",
            data={
                "version": version,
                "new_features": features,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
    
    # ============================================================================
    # Statistics and Monitoring
    # ============================================================================
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        active_tasks_count = len([t for t in self.active_tasks.values() if t["status"] in ["running", "starting"]])
        completed_tasks_count = len([t for t in self.active_tasks.values() if t["status"] == "completed"])
        failed_tasks_count = len([t for t in self.active_tasks.values() if t["status"] == "failed"])
        
        ws_stats = websocket_manager.get_connection_stats()
        
        return {
            "tasks": {
                "active": active_tasks_count,
                "completed": completed_tasks_count,
                "failed": failed_tasks_count,
                "total": len(self.active_tasks)
            },
            "agents": {
                "total_agents": len(self.agent_status),
                "active_agents": len([a for a in self.agent_status.values() if a["status"] == "active"]),
                "agent_types": list(self.agent_status.keys())
            },
            "websockets": ws_stats,
            "system": {
                "uptime": "N/A",  # Would be calculated from startup time
                "version": "1.0.0",
                "last_update": datetime.utcnow().isoformat()
            }
        }

# Global integration service instance
integration_service = AgentIntegrationService()
