"""
Task Management Routes
=====================

FastAPI routes for monitoring and controlling background tasks.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
import logging

from ..models import BaseResponse, PaginationParams
from ..auth import get_current_user
from ..services.integration_service import integration_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# Task Status and Monitoring
# ============================================================================

@router.get("/", response_model=BaseResponse)
async def list_tasks(
    pagination: PaginationParams = Depends(),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    List active tasks for the current user.
    
    Args:
        pagination: Pagination parameters
        current_user: Authenticated user
        
    Returns:
        BaseResponse: List of user's tasks
    """
    logger.info(f"Listing tasks for user: {current_user['username']}")
    
    try:
        # Get tasks for current user
        tasks = await integration_service.list_active_tasks(current_user["user_id"])
        
        # Apply pagination
        start_idx = (pagination.page - 1) * pagination.page_size
        end_idx = start_idx + pagination.page_size
        paginated_tasks = tasks[start_idx:end_idx]
        
        return BaseResponse(
            message="Tasks retrieved successfully",
            **{
                "tasks": paginated_tasks,
                "total": len(tasks),
                "page": pagination.page,
                "page_size": pagination.page_size
            }
        )
        
    except Exception as e:
        logger.error(f"Task listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )

@router.get("/{task_id}", response_model=BaseResponse)
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get status of a specific task.
    
    Args:
        task_id: Task identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Task status information
    """
    logger.info(f"Getting task status for: {task_id}")
    
    try:
        task_status = await integration_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if user owns this task
        if task_status.get("user_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        return BaseResponse(
            message="Task status retrieved successfully",
            **{"task": task_status}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}"
        )

@router.post("/{task_id}/cancel", response_model=BaseResponse)
async def cancel_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Cancel a running task.
    
    Args:
        task_id: Task identifier
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Cancellation confirmation
    """
    logger.info(f"Cancelling task: {task_id}")
    
    try:
        # Get task to check ownership
        task_status = await integration_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if user owns this task
        if task_status.get("user_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        # Check if task can be cancelled
        if task_status.get("status") in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task with status: {task_status.get('status')}"
            )
        
        # Cancel the task
        cancelled = await integration_service.cancel_task(task_id)
        
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel task"
            )
        
        return BaseResponse(
            message=f"Task {task_id} cancelled successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task cancellation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )

# ============================================================================
# System Statistics
# ============================================================================

@router.get("/system/stats", response_model=BaseResponse)
async def get_system_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get system-wide task and agent statistics (admin only).
    
    Args:
        current_user: Authenticated user (must be admin)
        
    Returns:
        BaseResponse: System statistics
    """
    # Check admin privileges
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    logger.info(f"Getting system stats for admin: {current_user['username']}")
    
    try:
        stats = integration_service.get_system_stats()
        
        return BaseResponse(
            message="System statistics retrieved successfully",
            **{"stats": stats}
        )
        
    except Exception as e:
        logger.error(f"System stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )

@router.get("/agents/status", response_model=BaseResponse)
async def get_agents_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Get current status of all agents.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        BaseResponse: Agent status information
    """
    logger.info(f"Getting agent status for user: {current_user['username']}")
    
    try:
        agent_status = await integration_service.get_agent_status()
        
        return BaseResponse(
            message="Agent status retrieved successfully",
            **{"agents": agent_status}
        )
        
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent status: {str(e)}"
        )

# ============================================================================
# System Notifications (Admin Only)
# ============================================================================

@router.post("/system/maintenance", response_model=BaseResponse)
async def notify_maintenance(
    maintenance_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Send system maintenance notification (admin only).
    
    Args:
        maintenance_data: Maintenance notification data
        current_user: Authenticated user (must be admin)
        
    Returns:
        BaseResponse: Notification confirmation
    """
    # Check admin privileges
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    logger.info(f"Sending maintenance notification by admin: {current_user['username']}")
    
    try:
        message = maintenance_data.get("message", "System maintenance scheduled")
        duration = maintenance_data.get("duration_minutes", 5)
        
        await integration_service.notify_system_maintenance(message, duration)
        
        return BaseResponse(
            message="Maintenance notification sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Maintenance notification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send maintenance notification: {str(e)}"
        )

@router.post("/system/update", response_model=BaseResponse)
async def notify_system_update(
    update_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BaseResponse:
    """
    Send system update notification (admin only).
    
    Args:
        update_data: Update notification data
        current_user: Authenticated user (must be admin)
        
    Returns:
        BaseResponse: Notification confirmation
    """
    # Check admin privileges
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    logger.info(f"Sending update notification by admin: {current_user['username']}")
    
    try:
        version = update_data.get("version", "1.0.0")
        features = update_data.get("features", [])
        
        await integration_service.notify_system_update(version, features)
        
        return BaseResponse(
            message="Update notification sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Update notification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send update notification: {str(e)}"
        )

# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def tasks_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for task management system.
    
    Returns:
        dict: Task management system health status
    """
    return {
        "status": "healthy",
        "service": "Task Management System",
        "features": [
            "Task Status Monitoring",
            "Task Cancellation",
            "System Statistics",
            "Agent Status Tracking",
            "Real-time Notifications",
            "Background Task Management"
        ],
        "endpoints": {
            "list": "GET /api/tasks/",
            "status": "GET /api/tasks/{id}",
            "cancel": "POST /api/tasks/{id}/cancel",
            "system_stats": "GET /api/tasks/system/stats",
            "agents_status": "GET /api/tasks/agents/status",
            "maintenance": "POST /api/tasks/system/maintenance",
            "update": "POST /api/tasks/system/update"
        }
    }
