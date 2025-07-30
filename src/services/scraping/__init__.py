"""
Scraping Services - Phase 6 Real-Time Web Scraping Implementation

This package provides real-time blog discovery and analysis capabilities using
free tools and APIs to replace mock data with actual scraped content.
"""

from .blog_scraper import BlogScraper, BlogSearchRequest, BlogResult, ScrapingProgress, blog_scraper
from .search_engines import SearchEngineManager
from .authority_scorer import AuthorityScorer
from .content_analyzer import ContentAnalyzer
from .rate_limiter import RateLimiter
from .data_validator import DataValidator

__all__ = [
    'BlogScraper',
    'BlogSearchRequest', 
    'BlogResult',
    'ScrapingProgress',
    'blog_scraper',
    'SearchEngineManager',
    'AuthorityScorer',
    'ContentAnalyzer',
    'RateLimiter',
    'DataValidator'
]

__version__ = '1.0.0'
