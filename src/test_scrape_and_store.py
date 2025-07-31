#!/usr/bin/env python3
"""
Test Bun Integration with Database Storage
-----------------------------------------

This script tests URL scraping with the Bun service and ensures the data is stored in the database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from api.services.integration_service import bun_integration_service
from seo_automation.utils.database import db_manager, Blog, BlogPost


async def test_scrape_and_store():
    """Test scraping a URL and storing results in the database"""
    test_url = "https://example.com"
    
    print(f"🌐 Testing URL scraping: {test_url}")
    result = await bun_integration_service.scrape_and_store_url(test_url)
    print(f"Scraping Result: {result}\n")
    
    if not result.get('success'):
        print("❌ Scraping failed")
        return
    
    # Verify data persistence in the database
    if db_manager.connection_available:
        session = db_manager.get_session()
        if session:
            try:
                blog_count = session.query(Blog).count()
                post_count = session.query(BlogPost).count()
                
                print(f"✅ Found {blog_count} blog(s) and {post_count} post(s) in the database")
                
                assert blog_count > 0 and post_count > 0
                print("🎉 Test completed successfully! Data is stored in the database.")
                
            except Exception as e:
                print(f"❌ Error querying database: {e}")
            finally:
                session.close()
        else:
            print("❌ Failed to create database session")
    else:
        print("❌ Database connection not available")

    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_scrape_and_store())

