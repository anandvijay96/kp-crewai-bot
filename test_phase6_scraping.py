"""
Test Script for Phase 6 Real-Time Scraping Implementation
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.scraping import blog_scraper, BlogSearchRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_blog_scraping():
    """Test the blog scraping functionality"""
    
    print("🚀 Testing Phase 6 Real-Time Blog Scraping")
    print("=" * 50)
    
    # Create a test search request
    search_request = BlogSearchRequest(
        keywords=["cloud computing", "devops"],
        min_domain_authority=30,
        min_page_authority=25,
        max_results=10
    )
    
    print(f"📝 Search Request:")
    print(f"   Keywords: {search_request.keywords}")
    print(f"   Min DA: {search_request.min_domain_authority}")
    print(f"   Min PA: {search_request.min_page_authority}")
    print(f"   Max Results: {search_request.max_results}")
    print()
    
    # Start the research
    print("🔍 Starting blog research...")
    task_id = await blog_scraper.start_research(search_request)
    print(f"   Task ID: {task_id}")
    print()
    
    # Monitor progress
    print("📊 Monitoring progress...")
    while True:
        progress = blog_scraper.get_progress(task_id)
        if not progress:
            print("❌ Task not found")
            break
        
        print(f"   Status: {progress['status']}")
        print(f"   Progress: {progress['progress_percentage']:.1f}%")
        print(f"   Current Step: {progress['current_step']}")
        print(f"   Found Blogs: {progress['found_blogs']}")
        print(f"   Validated Blogs: {progress['validated_blogs']}")
        
        if progress['errors']:
            print(f"   Errors: {len(progress['errors'])}")
            for error in progress['errors'][:3]:  # Show first 3 errors
                print(f"     - {error}")
        
        if progress['status'] in ['completed', 'failed']:
            break
        
        print("   Waiting...")
        await asyncio.sleep(2)
        print()
    
    # Get results
    if progress and progress['status'] == 'completed':
        print("✅ Research completed! Getting results...")
        results = blog_scraper.get_results(task_id)
        
        if results:
            print(f"🎉 Found {len(results)} validated blogs:")
            print()
            
            for i, result in enumerate(results[:5], 1):  # Show first 5 results
                print(f"   {i}. {result['title']}")
                print(f"      URL: {result['url']}")
                print(f"      Domain: {result['domain']}")
                print(f"      DA: {result.get('domain_authority', 'N/A')}")
                print(f"      PA: {result.get('page_authority', 'N/A')}")
                print(f"      Quality Score: {result.get('content_quality_score', 'N/A')}")
                print(f"      Category: {result.get('category', 'N/A')}")
                print(f"      Comment Opportunities: {len(result.get('comment_opportunities', []))}")
                print(f"      Source: {result.get('discovery_source', 'unknown')}")
                print()
            
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more results")
        else:
            print("❌ No results found")
    else:
        print(f"❌ Research failed with status: {progress['status'] if progress else 'unknown'}")
    
    print()
    print("🧹 Cleaning up...")
    blog_scraper.cleanup_old_tasks(max_age_hours=0)  # Clean up immediately for testing
    
    print("✅ Test completed!")

async def test_rate_limiting():
    """Test the rate limiting functionality"""
    
    print("🚀 Testing Rate Limiting")
    print("=" * 30)
    
    from services.scraping.rate_limiter import RateLimiter
    
    rate_limiter = RateLimiter()
    
    # Test getting status
    print("📊 Rate Limit Status:")
    status = rate_limiter.get_all_status()
    for service, info in status.items():
        print(f"   {service}: {info['requests_remaining']}/{info['rate_limit']} remaining")
    
    print()
    print("⏱️  Testing rate limiting...")
    
    # Test waiting for rate limit
    import time
    start_time = time.time()
    await rate_limiter.wait_if_needed('search_engines')
    await rate_limiter.wait_if_needed('search_engines')
    end_time = time.time()
    
    print(f"   Two requests took {end_time - start_time:.2f} seconds")
    print("✅ Rate limiting test completed!")

async def main():
    """Main test function"""
    
    try:
        # Test rate limiting first (quick test)
        await test_rate_limiting()
        print()
        
        # Test blog scraping (longer test)
        await test_blog_scraping()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.exception("Test failed")

if __name__ == "__main__":
    asyncio.run(main())
