"""
API Models and Schemas
======================

Pydantic models for request/response validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum

# ============================================================================
# Enums
# ============================================================================

class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class CommentStyle(str, Enum):
    """Comment style enumeration."""
    ENGAGING = "engaging"
    QUESTION = "question"
    INSIGHT = "insight"
    TECHNICAL = "technical"

class AgentType(str, Enum):
    """Agent type enumeration."""
    BLOG_RESEARCHER = "blog_researcher"
    COMMENT_WRITER = "comment_writer"
    QUALITY_REVIEWER = "quality_reviewer"
    CAMPAIGN_MANAGER = "campaign_manager"

# ============================================================================
# Base Models
# ============================================================================

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# ============================================================================
# Authentication Models
# ============================================================================

class UserLogin(BaseModel):
    """User login request model."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserRegister(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)

class TokenResponse(BaseResponse):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

# ============================================================================
# Campaign Models
# ============================================================================

class CampaignCreate(BaseModel):
    """Campaign creation request model."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    keywords: List[str] = Field(..., min_items=1, max_items=50)
    target_blogs: Optional[List[str]] = Field(None, max_items=100)
    comment_styles: List[CommentStyle] = Field(default=[CommentStyle.ENGAGING])
    max_blogs: int = Field(default=10, ge=1, le=100)
    max_comments_per_blog: int = Field(default=3, ge=1, le=10)
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    budget_limit: Optional[float] = Field(None, ge=0.0)
    
    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords list."""
        if not v:
            raise ValueError('At least one keyword is required')
        return [keyword.strip().lower() for keyword in v if keyword.strip()]

class CampaignUpdate(BaseModel):
    """Campaign update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[CampaignStatus] = None
    quality_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    budget_limit: Optional[float] = Field(None, ge=0.0)

class CampaignResponse(BaseResponse):
    """Campaign response model."""
    campaign: Dict[str, Any]

class CampaignListResponse(BaseResponse):
    """Campaign list response model."""
    campaigns: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int

# ============================================================================
# Blog Research Models
# ============================================================================

class BlogResearchRequest(BaseModel):
    """Blog research request model."""
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    max_results: int = Field(default=10, ge=1, le=50)
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    target_domains: Optional[List[str]] = Field(None, max_items=20)
    exclude_domains: Optional[List[str]] = Field(None, max_items=50)

class BlogInfo(BaseModel):
    """Blog information model."""
    url: str
    title: str
    description: Optional[str] = None
    domain: str
    authority_score: float
    quality_score: float
    comment_opportunity: bool
    seo_metrics: Dict[str, Any]
    discovered_at: datetime

class BlogResearchResponse(BaseResponse):
    """Blog research response model."""
    blogs: List[BlogInfo]
    total_discovered: int
    quality_filtered: int
    keywords_used: List[str]
    execution_time: float
    cost: float

# ============================================================================
# Comment Generation Models
# ============================================================================

class CommentGenerationRequest(BaseModel):
    """Comment generation request model."""
    blog_url: str = Field(..., pattern=r'^https?://.+')
    blog_content: Optional[str] = None
    style: CommentStyle = CommentStyle.ENGAGING
    max_comments: int = Field(default=3, ge=1, le=10)
    keywords: Optional[List[str]] = Field(None, max_items=10)
    custom_instructions: Optional[str] = Field(None, max_length=500)

class CommentInfo(BaseModel):
    """Comment information model."""
    id: str
    content: str
    style: CommentStyle
    quality_score: float
    engagement_potential: float
    keyword_density: float
    readability_score: float
    risk_assessment: Dict[str, Any]
    generated_at: datetime

class CommentGenerationResponse(BaseResponse):
    """Comment generation response model."""
    comments: List[CommentInfo]
    blog_url: str
    generation_stats: Dict[str, Any]
    execution_time: float
    cost: float

# ============================================================================
# Agent Models
# ============================================================================

class AgentStatus(BaseModel):
    """Agent status model."""
    agent_type: AgentType
    status: str
    last_activity: datetime
    performance_metrics: Dict[str, Any]
    resource_usage: Dict[str, Any]
    error_count: int
    success_rate: float

class AgentStatusResponse(BaseResponse):
    """Agent status response model."""
    agents: List[AgentStatus]

class AgentExecuteRequest(BaseModel):
    """Agent execution request model."""
    agent_type: AgentType
    task_config: Dict[str, Any]
    priority: int = Field(default=1, ge=1, le=10)
    timeout: Optional[int] = Field(None, ge=30, le=3600)

class AgentExecuteResponse(BaseResponse):
    """Agent execution response model."""
    task_id: str
    agent_type: AgentType
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None

# ============================================================================
# Analytics Models
# ============================================================================

class AnalyticsRequest(BaseModel):
    """Analytics request model."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    campaign_ids: Optional[List[str]] = None
    metrics: List[str] = Field(default=["campaigns", "blogs", "comments", "costs"])

class AnalyticsResponse(BaseResponse):
    """Analytics response model."""
    data: Dict[str, Any]
    period: Dict[str, datetime]
    summary: Dict[str, Union[int, float, str]]

# ============================================================================
# WebSocket Models
# ============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    channel: Optional[str] = None

class CampaignUpdate(BaseModel):
    """Campaign update notification model."""
    campaign_id: str
    status: CampaignStatus
    progress: float = Field(ge=0.0, le=1.0)
    current_task: Optional[str] = None
    metrics: Dict[str, Any]
    message: Optional[str] = None

# ============================================================================
# Pagination Models
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters model."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="desc", pattern=r'^(asc|desc)$')

class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
