"""
Blog Scraper - Main orchestrator for real-time blog discovery and analysis
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

from .search_engines import SearchEngineManager
from .authority_scorer import AuthorityScorer
from .content_analyzer import ContentAnalyzer
from .rate_limiter import RateLimiter
from .data_validator import DataValidator

logger = logging.getLogger(__name__)

@dataclass
class BlogSearchRequest:
    """Request configuration for blog search"""
    keywords: List[str]
    min_domain_authority: int = 30
    min_page_authority: int = 30
    max_results: int = 50
    categories: List[str] = None
    language: str = "en"
    region: str = "US"
    exclude_domains: Set[str] = None

@dataclass
class BlogResult:
    """Individual blog discovery result"""
    url: str
    domain: str
    title: str
    description: str
    domain_authority: Optional[int] = None
    page_authority: Optional[int] = None
    category: Optional[str] = None
    publish_date: Optional[datetime] = None
    author: Optional[str] = None
    content_quality_score: Optional[float] = None
    comment_opportunities: Optional[List[str]] = None
    discovery_source: str = "unknown"
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()

@dataclass  
class ScrapingProgress:
    """Progress tracking for scraping operations"""
    task_id: str
    status: str  # 'started', 'searching', 'analyzing', 'completed', 'failed'
    total_expected: int = 0
    completed: int = 0
    found_blogs: int = 0
    validated_blogs: int = 0
    current_step: str = ""
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()
        if self.errors is None:
            self.errors = []
    
    @property
    def progress_percentage(self) -> float:
        if self.total_expected == 0:
            return 0.0
        return min(100.0, (self.completed / self.total_expected) * 100)

class BlogScraper:
    """
    Main orchestrator for real-time blog discovery and analysis
    Coordinates search engines, authority scoring, and content analysis
    """
    
    def __init__(self):
        self.search_manager = SearchEngineManager()
        self.authority_scorer = AuthorityScorer()
        self.content_analyzer = ContentAnalyzer()
        self.rate_limiter = RateLimiter()
        self.data_validator = DataValidator()
        
        # Progress tracking
        self.active_tasks: Dict[str, ScrapingProgress] = {}
        
        # Configuration
        self.max_concurrent_requests = 5
        self.timeout_seconds = 300  # 5 minutes
        
    async def start_research(
        self,
        request: BlogSearchRequest,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Start a new blog research task
        Returns task_id for progress tracking
        """
        task_id = f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        progress = ScrapingProgress(
            task_id=task_id,
            status="started",
            current_step="Initializing search"
        )
        
        self.active_tasks[task_id] = progress
        
        # Start the research process in background
        asyncio.create_task(
            self._execute_research(task_id, request, progress_callback)
        )
        
        return task_id
    
    async def _execute_research(
        self,
        task_id: str,
        request: BlogSearchRequest,
        progress_callback: Optional[callable] = None
    ):
        """Execute the complete research workflow"""
        progress = self.active_tasks[task_id]
        
        try:
            # Step 1: Search for blogs across multiple sources
            progress.status = "searching"
            progress.current_step = "Searching across multiple engines"
            await self._notify_progress(progress, progress_callback)
            
            raw_results = await self._search_blogs(request, progress)
            progress.total_expected = len(raw_results)
            progress.found_blogs = len(raw_results)
            
            # Step 2: Analyze and score each blog
            progress.status = "analyzing"
            progress.current_step = "Analyzing blog quality and authority"
            await self._notify_progress(progress, progress_callback)
            
            analyzed_results = await self._analyze_blogs(
                raw_results, request, progress, progress_callback
            )
            
            # Step 3: Filter and rank results
            progress.current_step = "Filtering and ranking results"
            await self._notify_progress(progress, progress_callback)
            
            final_results = await self._filter_and_rank(
                analyzed_results, request
            )
            
            progress.validated_blogs = len(final_results)
            progress.completed = len(final_results)
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            progress.current_step = f"Found {len(final_results)} qualified blogs"
            
            # Store results in progress object
            progress.results = final_results
            
            await self._notify_progress(progress, progress_callback)
            
        except Exception as e:
            logger.error(f"Research task {task_id} failed: {str(e)}")
            progress.status = "failed"
            progress.errors.append(str(e))
            progress.completed_at = datetime.utcnow()
            await self._notify_progress(progress, progress_callback)
    
    async def _search_blogs(
        self,
        request: BlogSearchRequest,
        progress: ScrapingProgress
    ) -> List[Dict[str, Any]]:
        """Search for blogs across multiple search engines"""
        all_results = []
        
        # Search each keyword across all available engines
        for keyword in request.keywords:
            try:
                # Google Custom Search
                google_results = await self.search_manager.search_google(
                    query=keyword,
                    max_results=request.max_results // len(request.keywords),
                    region=request.region,
                    language=request.language
                )
                all_results.extend(google_results)
                
                # Note: Bing Search removed for simplicity
                # Can be added back in future phases
                
                # DuckDuckGo Search
                ddg_results = await self.search_manager.search_duckduckgo(
                    query=keyword,
                    max_results=request.max_results // len(request.keywords)
                )
                all_results.extend(ddg_results)
                
                # Apply rate limiting between searches
                await self.rate_limiter.wait_if_needed("search_engines")
                
            except Exception as e:
                logger.warning(f"Search failed for keyword '{keyword}': {str(e)}")
                progress.errors.append(f"Search failed for '{keyword}': {str(e)}")
        
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        
        for result in all_results:
            url = result.get('url', '').lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    async def _analyze_blogs(
        self,
        raw_results: List[Dict[str, Any]],
        request: BlogSearchRequest,
        progress: ScrapingProgress,
        progress_callback: Optional[callable] = None
    ) -> List[BlogResult]:
        """Analyze each blog for authority, quality, and opportunities"""
        analyzed_results = []
        
        # Process blogs in batches to avoid overwhelming services
        batch_size = self.max_concurrent_requests
        
        for i in range(0, len(raw_results), batch_size):
            batch = raw_results[i:i + batch_size]
            batch_tasks = []
            
            for raw_result in batch:
                task = self._analyze_single_blog(raw_result, request)
                batch_tasks.append(task)
            
            # Process batch concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.warning(f"Blog analysis failed: {str(result)}")
                    progress.errors.append(f"Analysis failed: {str(result)}")
                elif result is not None:
                    analyzed_results.append(result)
                    progress.completed += 1
                    
                    # Notify progress periodically
                    if progress_callback and progress.completed % 5 == 0:
                        await self._notify_progress(progress, progress_callback)
            
            # Rate limiting between batches
            await self.rate_limiter.wait_if_needed("authority_scoring")
        
        return analyzed_results
    
    async def _analyze_single_blog(
        self,
        raw_result: Dict[str, Any],
        request: BlogSearchRequest
    ) -> Optional[BlogResult]:
        """Analyze a single blog for all metrics"""
        try:
            url = raw_result.get('url')
            domain = raw_result.get('domain')
            
            if not url or not domain:
                return None
            
            # Skip excluded domains
            if request.exclude_domains and domain in request.exclude_domains:
                return None
            
            # Get authority scores
            authority_scores = await self.authority_scorer.get_authority_scores(domain)
            domain_authority = authority_scores.get('domain_authority')
            page_authority = authority_scores.get('page_authority')
            
            # Apply authority filters - enforce minimum DA/PA ≥ 30 requirement
            # Both DA and PA must meet minimum thresholds if available
            if domain_authority is not None and domain_authority < request.min_domain_authority:
                logger.debug(f"Blog {domain} rejected: DA {domain_authority} < {request.min_domain_authority}")
                return None
            if page_authority is not None and page_authority < request.min_page_authority:
                logger.debug(f"Blog {domain} rejected: PA {page_authority} < {request.min_page_authority}")
                return None
            
            # Ensure at least one authority score meets our requirements
            if not self.authority_scorer.meets_minimum_threshold(domain_authority, page_authority):
                logger.debug(f"Blog {domain} rejected: Neither DA ({domain_authority}) nor PA ({page_authority}) meets minimum threshold")
                return None
            
            # Analyze content quality and opportunities
            content_analysis = await self.content_analyzer.analyze_url(url)
            
            # Create result object
            blog_result = BlogResult(
                url=url,
                domain=domain,
                title=raw_result.get('title', ''),
                description=raw_result.get('description', ''),
                domain_authority=domain_authority,
                page_authority=page_authority,
                category=content_analysis.get('category'),
                publish_date=content_analysis.get('publish_date'),
                author=content_analysis.get('author'),
                content_quality_score=content_analysis.get('quality_score'),
                comment_opportunities=content_analysis.get('comment_opportunities', []),
                discovery_source=raw_result.get('source', 'unknown')
            )
            
            # Validate the result
            if self.data_validator.validate_blog_result(blog_result):
                return blog_result
            
        except Exception as e:
            logger.warning(f"Failed to analyze blog {raw_result.get('url')}: {str(e)}")
        
        return None
    
    async def _filter_and_rank(
        self,
        analyzed_results: List[BlogResult],
        request: BlogSearchRequest
    ) -> List[BlogResult]:
        """Filter and rank results based on quality metrics"""
        # Filter out low-quality results
        filtered_results = []
        
        for result in analyzed_results:
            # Quality score threshold
            if result.content_quality_score and result.content_quality_score < 0.6:
                continue
            
            # Must have comment opportunities
            if not result.comment_opportunities:
                continue
            
            # Authority scores must meet minimum requirements
            if result.domain_authority and result.domain_authority < request.min_domain_authority:
                continue
                
            if result.page_authority and result.page_authority < request.min_page_authority:
                continue
            
            filtered_results.append(result)
        
        # Rank by composite score
        def calculate_composite_score(blog: BlogResult) -> float:
            score = 0.0
            
            # Authority scores (40% weight)
            if blog.domain_authority:
                score += (blog.domain_authority / 100) * 0.25
            if blog.page_authority:
                score += (blog.page_authority / 100) * 0.15
            
            # Content quality (30% weight)
            if blog.content_quality_score:
                score += blog.content_quality_score * 0.30
            
            # Comment opportunities (20% weight)
            opportunities_score = min(len(blog.comment_opportunities) / 5, 1.0)
            score += opportunities_score * 0.20
            
            # Recency bonus (10% weight)
            if blog.publish_date:
                days_old = (datetime.utcnow() - blog.publish_date).days
                recency_score = max(0, 1 - (days_old / 365))  # Decay over a year
                score += recency_score * 0.10
            
            return score
        
        # Sort by composite score (descending)
        filtered_results.sort(key=calculate_composite_score, reverse=True)
        
        # Limit to requested max results
        return filtered_results[:request.max_results]
    
    async def _notify_progress(
        self,
        progress: ScrapingProgress,
        callback: Optional[callable] = None
    ):
        """Notify progress update via callback"""
        if callback:
            try:
                await callback(progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {str(e)}")
    
    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a task"""
        progress = self.active_tasks.get(task_id)
        if not progress:
            return None
        
        return {
            "task_id": progress.task_id,
            "status": progress.status,
            "progress_percentage": progress.progress_percentage,
            "current_step": progress.current_step,
            "found_blogs": progress.found_blogs,
            "validated_blogs": progress.validated_blogs,
            "started_at": progress.started_at.isoformat(),
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "errors": progress.errors
        }
    
    def get_results(self, task_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get final results for a completed task"""
        progress = self.active_tasks.get(task_id)
        if not progress or progress.status != "completed":
            return None
        
        results = getattr(progress, 'results', [])
        return [asdict(result) for result in results]
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, progress in self.active_tasks.items():
            if (progress.completed_at and 
                progress.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.active_tasks[task_id]
            
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")

# Singleton instance
blog_scraper = BlogScraper()
