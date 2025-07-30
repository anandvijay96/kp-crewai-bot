#!/usr/bin/env python3
"""
Test script for the new scraping infrastructure
Tests DA/PA filtering, search engines, and blog analysis
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.scraping.authority_scorer import AuthorityScorer
from services.scraping.search_engines import SearchEngineManager
from services.scraping.blog_scraper import BlogScraper, BlogSearchRequest
from services.scraping.content_analyzer import ContentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_authority_scorer():
    """Test the authority scoring with DA/PA minimum threshold"""
    logger.info("Testing Authority Scorer...")
    
    scorer = AuthorityScorer()
    
    # Test known domains with various authority levels
    test_domains = [
        "medium.com",       # Should have high authority
        "techcrunch.com",   # Should have high authority
        "example.com",      # Should have lower authority
        "randomnewblog.com" # Should have very low authority
    ]
    
    for domain in test_domains:
        try:
            scores = await scorer.get_authority_scores(domain)
            da = scores.get('domain_authority')
            pa = scores.get('page_authority')
            meets_threshold = scorer.meets_minimum_threshold(da, pa)
            
            logger.info(f"Domain: {domain}")
            logger.info(f"  DA: {da}, PA: {pa}")
            logger.info(f"  Meets threshold (≥30): {meets_threshold}")
            logger.info(f"  Filtered result: {'ACCEPTED' if meets_threshold else 'REJECTED'}")
            print()
            
        except Exception as e:
            logger.error(f"Failed to score {domain}: {str(e)}")
    
    # Test threshold configuration
    threshold_info = scorer.get_threshold_info()
    logger.info(f"Threshold configuration: {threshold_info}")
    
    await scorer.close()

async def test_search_engines():
    """Test search engine integration"""
    logger.info("Testing Search Engines...")
    
    async with SearchEngineManager() as search_manager:
        # Load API keys (will show warnings if not configured)
        search_manager._load_api_keys()
        
        # Test query
        test_query = "artificial intelligence blog"
        
        # Test Google search (will use simulation if API not configured)
        try:
            google_results = await search_manager.search_google(test_query, max_results=3)
            logger.info(f"Google results: {len(google_results)} blogs found")
            for i, result in enumerate(google_results[:2]):
                logger.info(f"  {i+1}. {result.get('title', 'No title')} - {result.get('domain', 'No domain')}")
        except Exception as e:
            logger.warning(f"Google search failed: {str(e)}")
        
        # Note: Bing search removed for simplicity
        
        # Test DuckDuckGo search
        try:
            ddg_results = await search_manager.search_duckduckgo(test_query, max_results=3)
            logger.info(f"DuckDuckGo results: {len(ddg_results)} blogs found")
            for i, result in enumerate(ddg_results[:2]):
                logger.info(f"  {i+1}. {result.get('title', 'No title')} - {result.get('domain', 'No domain')}")
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {str(e)}")

async def test_content_analyzer():
    """Test content analysis functionality"""
    logger.info("Testing Content Analyzer...")
    
    analyzer = ContentAnalyzer()
    
    # Test URLs (using well-known blog URLs)
    test_urls = [
        "https://medium.com/@example/test",
        "https://techcrunch.com/example-article",
        "https://example.com/blog/post"
    ]
    
    for url in test_urls:
        try:
            analysis = await analyzer.analyze_url(url)
            logger.info(f"URL: {url}")
            logger.info(f"  Quality Score: {analysis.get('quality_score')}")
            logger.info(f"  Category: {analysis.get('category')}")
            logger.info(f"  Comment Opportunities: {len(analysis.get('comment_opportunities', []))}")
            print()
        except Exception as e:
            logger.warning(f"Analysis failed for {url}: {str(e)}")

async def test_blog_scraper_integration():
    """Test the complete blog scraper workflow"""
    logger.info("Testing Complete Blog Scraper Integration...")
    
    scraper = BlogScraper()
    
    # Create a search request
    request = BlogSearchRequest(
        keywords=["machine learning blog", "AI tutorials"],
        min_domain_authority=30,  # Enforce DA ≥ 30
        min_page_authority=30,    # Enforce PA ≥ 30
        max_results=10,
        language="en",
        region="US"
    )
    
    logger.info(f"Search request: DA≥{request.min_domain_authority}, PA≥{request.min_page_authority}")
    
    # Progress callback to track progress
    async def progress_callback(progress):
        logger.info(f"Progress: {progress.progress_percentage:.1f}% - {progress.current_step}")
        if progress.errors:
            logger.warning(f"Errors: {progress.errors[-1]}")
    
    # Start research
    task_id = await scraper.start_research(request, progress_callback)
    logger.info(f"Started research task: {task_id}")
    
    # Wait for completion (with timeout)
    max_wait = 60  # 60 seconds timeout
    waited = 0
    
    while waited < max_wait:
        progress = scraper.get_progress(task_id)
        if not progress:
            logger.error("Task not found")
            break
        
        status = progress['status']
        logger.info(f"Status: {status} - {progress['current_step']}")
        
        if status in ['completed', 'failed']:
            break
        
        await asyncio.sleep(2)
        waited += 2
    
    # Get final results
    final_progress = scraper.get_progress(task_id)
    if final_progress:
        logger.info(f"Final status: {final_progress['status']}")
        logger.info(f"Found blogs: {final_progress['found_blogs']}")
        logger.info(f"Validated blogs: {final_progress['validated_blogs']}")
        
        if final_progress['status'] == 'completed':
            results = scraper.get_results(task_id)
            if results:
                logger.info(f"Final results: {len(results)} blogs passed DA/PA filtering")
                for i, blog in enumerate(results[:3]):  # Show first 3
                    logger.info(f"  {i+1}. {blog['title'][:50]}...")
                    logger.info(f"      Domain: {blog['domain']}")
                    logger.info(f"      DA: {blog['domain_authority']}, PA: {blog['page_authority']}")
                    logger.info(f"      Quality: {blog['content_quality_score']}")
            else:
                logger.warning("No results found")
        else:
            logger.error(f"Task failed with errors: {final_progress['errors']}")
    
    # Cleanup
    scraper.cleanup_old_tasks()

async def main():
    """Run all tests"""
    logger.info("=== Testing Scraping Infrastructure ===")
    
    try:
        # Test individual components
        await test_authority_scorer()
        print("=" * 60)
        
        await test_search_engines()
        print("=" * 60)
        
        await test_content_analyzer()
        print("=" * 60)
        
        # Test integration
        await test_blog_scraper_integration()
        
        logger.info("=== All tests completed ===")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
