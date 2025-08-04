"""
API Models Module
=================

Pydantic models for API request/response validation.
"""

from .api_models import (
    ApiResponse, ErrorResponse, AgentType, TaskStatus, BaseResponse,
    AgentStatusResponse, AgentExecuteRequest, AgentExecuteResponse
)
from .user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserRole, UserPermission,
    Token, TokenRefresh, PasswordReset, PasswordChange, ROLE_PERMISSIONS
)

from .comment import (
    CommentGenerationRequest, CommentGenerationResponse, CommentStyle,
    PaginationParams, GeneratedComment, CommentListItem, CommentListResponse,
    BatchCommentRequest, CommentReviewRequest, CommentRegenerateRequest
)
from .blog import (
    BlogResearchRequest, BlogResearchResponse, BlogStatus, BlogDiscoveryResult,
    BlogListItem, BlogListResponse, BlogAnalysisRequest, BlogAnalysisResponse,
    BlogUpdateRequest, BatchBlogAnalysisRequest
)
from .campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignStatus, CampaignSettings, CampaignMetrics
)

__all__ = [
    # API Models
    "ApiResponse",
    "ErrorResponse",
    "AgentType",
    "TaskStatus",
    "BaseResponse",
    "AgentStatusResponse",
    "AgentExecuteRequest",
    "AgentExecuteResponse",
    
    # User Models
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserLogin",
    "UserRole",
    "UserPermission",
    "Token",
    "TokenRefresh",
    "PasswordReset",
    "PasswordChange",
    "ROLE_PERMISSIONS",

    # Comment Models
    "CommentGenerationRequest",
    "CommentGenerationResponse",
    "CommentStyle",
    "PaginationParams",
    "GeneratedComment",
    "CommentListItem",
    "CommentListResponse",
    "BatchCommentRequest",
    "CommentReviewRequest",
    "CommentRegenerateRequest",

    # Blog Models
    "BlogResearchRequest",
    "BlogResearchResponse",
    "BlogStatus",
    "BlogDiscoveryResult",
    "BlogListItem",
    "BlogListResponse",
    "BlogAnalysisRequest",
    "BlogAnalysisResponse",
    "BlogUpdateRequest",
    "BatchBlogAnalysisRequest",

    # Campaign Models
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignListResponse",
    "CampaignStatus",
    "CampaignSettings",
    "CampaignMetrics"
]
