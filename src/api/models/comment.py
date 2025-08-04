"""
Comment API Models
==================

Pydantic models for comment generation API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class CommentStyle(str, Enum):
    """Comment generation styles."""
    ENGAGING = "engaging"
    QUESTION = "question"
    INSIGHT = "insight"
    TECHNICAL = "technical"


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class CommentGenerationRequest(BaseModel):
    """Request model for comment generation."""
    blog_url: HttpUrl = Field(..., description="URL of the blog post to comment on")
    max_comments: int = Field(default=3, ge=1, le=10, description="Maximum number of comments to generate")
    style: CommentStyle = Field(default=CommentStyle.ENGAGING, description="Style of comments to generate")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to focus on in comments")
    custom_instructions: Optional[str] = Field(default=None, description="Custom instructions for comment generation")
    author_persona: Optional[Dict[str, Any]] = Field(default=None, description="Author persona for comment generation")


class RiskAssessment(BaseModel):
    """Risk assessment for generated comments."""
    spam_likelihood: float = Field(..., ge=0, le=1, description="Likelihood of being flagged as spam")
    brand_safety: float = Field(..., ge=0, le=1, description="Brand safety score")
    authenticity_score: float = Field(..., ge=0, le=1, description="Authenticity score")
    policy_compliance: float = Field(..., ge=0, le=1, description="Policy compliance score")


class GeneratedComment(BaseModel):
    """Generated comment model."""
    id: str = Field(..., description="Unique comment identifier")
    content: str = Field(..., description="Comment content")
    style: CommentStyle = Field(..., description="Comment style")
    quality_score: float = Field(..., ge=0, le=1, description="Overall quality score")
    engagement_potential: float = Field(..., ge=0, le=1, description="Engagement potential score")
    keyword_density: float = Field(..., ge=0, le=1, description="Keyword density score")
    readability_score: float = Field(..., ge=0, le=1, description="Readability score")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment metrics")
    generated_at: datetime = Field(..., description="Generation timestamp")


class GenerationStats(BaseModel):
    """Statistics for comment generation."""
    total_generated: int = Field(..., description="Total comments generated")
    average_quality: float = Field(..., ge=0, le=1, description="Average quality score")
    style_distribution: Dict[str, int] = Field(..., description="Distribution of comment styles")
    keywords_used: List[str] = Field(..., description="Keywords used in generation")
    ai_model: str = Field(..., description="AI model used for generation")
    tokens_consumed: int = Field(..., description="Tokens consumed during generation")
    generation_iterations: int = Field(..., description="Number of generation iterations")


class CommentGenerationResponse(BaseModel):
    """Response model for comment generation."""
    comments: List[GeneratedComment] = Field(..., description="Generated comments")
    blog_url: str = Field(..., description="Blog URL that was commented on")
    generation_stats: GenerationStats = Field(..., description="Generation statistics")
    execution_time: float = Field(..., description="Execution time in seconds")
    cost: float = Field(..., description="Cost of generation in USD")
    message: str = Field(..., description="Response message")


class CommentListItem(BaseModel):
    """Comment list item for listing endpoints."""
    id: str = Field(..., description="Comment identifier")
    content: str = Field(..., description="Comment content (truncated)")
    style: str = Field(..., description="Comment style")
    quality_score: float = Field(..., ge=0, le=1, description="Quality score")
    blog_url: str = Field(..., description="Blog URL")
    blog_title: str = Field(..., description="Blog title")
    generated_at: str = Field(..., description="Generation timestamp")
    campaign_id: Optional[str] = Field(default=None, description="Associated campaign ID")
    status: str = Field(..., description="Comment status")


class CommentListResponse(BaseModel):
    """Response model for comment list endpoints."""
    comments: List[CommentListItem] = Field(..., description="List of comments")
    total: int = Field(..., description="Total number of comments")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    message: str = Field(..., description="Response message")


class BatchCommentRequest(BaseModel):
    """Request model for batch comment generation."""
    requests: List[CommentGenerationRequest] = Field(..., description="List of comment generation requests")
    priority: Optional[str] = Field(default="normal", description="Processing priority")
    notify_on_completion: Optional[bool] = Field(default=True, description="Send notification when complete")


class CommentReviewRequest(BaseModel):
    """Request model for comment review."""
    decision: str = Field(..., description="Review decision (approved/rejected/needs_revision)")
    feedback: Optional[str] = Field(default=None, description="Review feedback")
    quality_adjustments: Optional[Dict[str, Any]] = Field(default=None, description="Quality score adjustments")


class CommentRegenerateRequest(BaseModel):
    """Request model for comment regeneration."""
    style: Optional[CommentStyle] = Field(default=None, description="New comment style")
    custom_instructions: Optional[str] = Field(default=None, description="Updated custom instructions")
    keywords: Optional[List[str]] = Field(default=None, description="Updated keywords")
    improve_quality: Optional[bool] = Field(default=True, description="Focus on quality improvement")
