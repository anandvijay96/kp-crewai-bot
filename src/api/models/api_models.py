"""
API Models
==========

Core API response models for consistent response formatting.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


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
