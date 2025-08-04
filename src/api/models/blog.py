"""
Blog API Models
===============

Pydantic models for blog-related API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class BlogStatus(str, Enum):
    """Blog processing status."""
    DISCOVERED = "discovered"
    ANALYZED = "analyzed"
    APPROVED = "approved"
    COMMENTED = "commented"
    REJECTED = "rejected"


class BlogResearchRequest(BaseModel):
    """Request model for blog research and discovery."""
    keywords: List[str] = Field(..., description="Keywords to search for")
    max_results: Optional[int] = Field(default=50, ge=1, le=200, description="Maximum number of blogs to discover")
    min_quality_score: Optional[float] = Field(default=0.6, ge=0, le=1, description="Minimum quality score filter")
    target_domains: Optional[List[str]] = Field(default=None, description="Specific domains to target")
    excluded_domains: Optional[List[str]] = Field(default=None, description="Domains to exclude")
    language: Optional[str] = Field(default="en", description="Content language")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Date range filter")


class BlogAnalysisMetrics(BaseModel):
    """Blog analysis metrics."""
    content_quality: float = Field(..., ge=0, le=1, description="Content quality score")
    seo_score: float = Field(..., ge=0, le=1, description="SEO optimization score")
    readability_score: float = Field(..., ge=0, le=1, description="Content readability score")
    authority_score: float = Field(..., ge=0, le=1, description="Domain authority score")
    comment_opportunity_score: float = Field(..., ge=0, le=1, description="Comment opportunity score")
    engagement_potential: float = Field(..., ge=0, le=1, description="Engagement potential score")


class BlogContent(BaseModel):
    """Blog content analysis."""
    title: str = Field(..., description="Blog post title")
    meta_description: Optional[str] = Field(default=None, description="Meta description")
    content_snippet: str = Field(..., description="Content snippet or summary")
    word_count: int = Field(..., description="Total word count")
    headings: List[str] = Field(default=[], description="Extracted headings")
    images_count: int = Field(default=0, description="Number of images")
    links_count: int = Field(default=0, description="Number of links")


class BlogDiscoveryResult(BaseModel):
    """Individual blog discovery result."""
    id: str = Field(..., description="Unique blog identifier")
    url: HttpUrl = Field(..., description="Blog post URL")
    domain: str = Field(..., description="Domain name")
    title: str = Field(..., description="Blog post title")
    content: BlogContent = Field(..., description="Blog content analysis")
    metrics: BlogAnalysisMetrics = Field(..., description="Analysis metrics")
    keywords: List[str] = Field(..., description="Matched keywords")
    discovered_at: datetime = Field(..., description="Discovery timestamp")
    status: BlogStatus = Field(default=BlogStatus.DISCOVERED, description="Processing status")
    rejection_reason: Optional[str] = Field(default=None, description="Rejection reason if rejected")


class BlogResearchResponse(BaseModel):
    """Response model for blog research."""
    blogs: List[BlogDiscoveryResult] = Field(..., description="Discovered blogs")
    total_discovered: int = Field(..., description="Total blogs discovered")
    search_keywords: List[str] = Field(..., description="Keywords used in search")
    search_stats: Dict[str, Any] = Field(..., description="Search statistics")
    execution_time: float = Field(..., description="Search execution time in seconds")
    cost: float = Field(..., description="Search cost in USD")
    message: str = Field(..., description="Response message")


class BlogListItem(BaseModel):
    """Blog list item for listing endpoints."""
    id: str = Field(..., description="Blog identifier")
    url: str = Field(..., description="Blog URL")
    title: str = Field(..., description="Blog title")
    domain: str = Field(..., description="Domain")
    quality_score: float = Field(..., description="Overall quality score")
    status: str = Field(..., description="Processing status")
    discovered_at: str = Field(..., description="Discovery timestamp")
    keywords: List[str] = Field(..., description="Associated keywords")


class BlogListResponse(BaseModel):
    """Response model for blog list endpoints."""
    blogs: List[BlogListItem] = Field(..., description="List of blogs")
    total: int = Field(..., description="Total number of blogs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    filters_applied: Dict[str, Any] = Field(default={}, description="Applied filters")
    message: str = Field(..., description="Response message")


class BlogAnalysisRequest(BaseModel):
    """Request model for individual blog analysis."""
    blog_url: HttpUrl = Field(..., description="Blog URL to analyze")
    force_reanalysis: Optional[bool] = Field(default=False, description="Force re-analysis if already analyzed")
    include_content: Optional[bool] = Field(default=True, description="Include full content analysis")


class BlogAnalysisResponse(BaseModel):
    """Response model for blog analysis."""
    blog: BlogDiscoveryResult = Field(..., description="Analyzed blog")
    analysis_details: Dict[str, Any] = Field(..., description="Detailed analysis breakdown")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    execution_time: float = Field(..., description="Analysis execution time in seconds")
    message: str = Field(..., description="Response message")


class BlogUpdateRequest(BaseModel):
    """Request model for updating blog status."""
    status: BlogStatus = Field(..., description="New blog status")
    rejection_reason: Optional[str] = Field(default=None, description="Rejection reason if rejecting")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class BatchBlogAnalysisRequest(BaseModel):
    """Request model for batch blog analysis."""
    blog_urls: List[HttpUrl] = Field(..., description="List of blog URLs to analyze")
    priority: Optional[str] = Field(default="normal", description="Processing priority")
    notify_on_completion: Optional[bool] = Field(default=True, description="Send notification when complete")
