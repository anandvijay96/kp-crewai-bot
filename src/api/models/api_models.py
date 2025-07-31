"""
API Models
==========

Core API response models for consistent response formatting.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ApiResponse(BaseModel):
    """Standard API response model."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"key": "value"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str = "An error occurred"
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "An error occurred",
                "error": "ValidationError",
                "details": {"field": "error description"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class AgentType(str, Enum):
    """Enum for agent types."""
    BLOG_RESEARCHER = "blog_researcher"
    COMMENT_WRITER = "comment_writer"
    QUALITY_REVIEWER = "quality_reviewer"
    CAMPAIGN_MANAGER = "campaign_manager"


class TaskStatus(str, Enum):
    """Enum for task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model."""
    message: str = "Operation successful"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentStatusResponse(BaseModel):
    """Agent status response model."""
    agents: List[Dict[str, Any]]
    message: str = "Agent status retrieved successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentExecuteRequest(BaseModel):
    """Agent execution request model."""
    agent_type: AgentType
    task_data: Dict[str, Any]
    priority: Optional[int] = 1
    timeout: Optional[int] = 300


class AgentExecuteResponse(BaseModel):
    """Agent execution response model."""
    task_id: str
    agent_type: str
    status: TaskStatus
    message: str
    result: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
