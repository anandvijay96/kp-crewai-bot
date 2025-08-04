"""
Campaign API Models
===================

Pydantic models for campaign-related API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"


class CampaignSettings(BaseModel):
    """Campaign configuration settings."""
    max_blogs_per_keyword: int = Field(default=50, ge=1, le=200, description="Maximum blogs to discover per keyword")
    min_blog_quality_score: float = Field(default=0.6, ge=0, le=1, description="Minimum blog quality threshold")
    comment_style: str = Field(default="professional", description="Default comment style")
    auto_post: bool = Field(default=False, description="Enable automatic comment posting")
    posting_delay: int = Field(default=300, ge=0, description="Delay between posts in seconds")
    target_domains: Optional[List[str]] = Field(default=None, description="Target specific domains")
    excluded_domains: Optional[List[str]] = Field(default=None, description="Domains to exclude")


class CampaignCreate(BaseModel):
    """Request model for creating campaigns."""
    name: str = Field(..., min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Campaign description")
    keywords: List[str] = Field(..., min_items=1, description="Campaign keywords")
    settings: CampaignSettings = Field(..., description="Campaign configuration")


class CampaignUpdate(BaseModel):
    """Request model for updating campaigns."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Campaign description")
    keywords: Optional[List[str]] = Field(default=None, min_items=1, description="Campaign keywords")
    settings: Optional[CampaignSettings] = Field(default=None, description="Campaign configuration")
    status: Optional[CampaignStatus] = Field(default=None, description="Campaign status")


class CampaignMetrics(BaseModel):
    """Campaign performance metrics."""
    total_blogs: int = Field(default=0, description="Total blogs discovered")
    comments_generated: int = Field(default=0, description="Total comments generated")
    comments_posted: int = Field(default=0, description="Total comments posted")
    success_rate: float = Field(default=0.0, ge=0, le=1, description="Success rate percentage")
    avg_quality_score: float = Field(default=0.0, ge=0, le=1, description="Average comment quality")
    total_cost: float = Field(default=0.0, description="Total campaign cost in USD")


class CampaignResponse(BaseModel):
    """Response model for campaign operations."""
    id: str = Field(..., description="Campaign identifier")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(default=None, description="Campaign description")
    keywords: List[str] = Field(..., description="Campaign keywords")
    status: CampaignStatus = Field(..., description="Campaign status")
    settings: CampaignSettings = Field(..., description="Campaign settings")
    metrics: CampaignMetrics = Field(..., description="Campaign metrics")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator username")


class CampaignListResponse(BaseModel):
    """Response model for campaign list endpoints."""
    campaigns: List[CampaignResponse] = Field(..., description="List of campaigns")
    total: int = Field(..., description="Total number of campaigns")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    message: str = Field(..., description="Response message")
