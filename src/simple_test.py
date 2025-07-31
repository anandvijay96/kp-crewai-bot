#!/usr/bin/env python3
"""
Simple test to verify Bun scraping and database storage
"""
import sqlite3
import requests
import json

def test_database():
    """Test database connection and tables"""
    print("🗃️ Testing database connection...")
    try:
        conn = sqlite3.connect('./seo_automation.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Check existing data
        cursor.execute("SELECT COUNT(*) FROM blogs")
        blog_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blog_posts")  
        post_count = cursor.fetchone()[0]
        
        print(f"✅ Database contains {blog_count} blogs and {post_count} posts")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_bun_service():
    """Test Bun service directly"""
    print("🌐 Testing Bun service...")
    try:
        # Test scraping endpoint
        response = requests.post(
            'http://localhost:3001/api/scraping/scrape',
            json={'url': 'https://httpbin.org/html'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Bun scraping successful! Title: {data['data'].get('title', 'No title')}")
                return data
            else:
                print(f"❌ Bun scraping failed: {data}")
                return None
        else:
            print(f"❌ Bun service error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Bun service test failed: {e}")
        return None

def test_database_insertion(scraped_data):
    """Test inserting scraped data into database"""
    print("💾 Testing database insertion...")
    try:
        conn = sqlite3.connect('./seo_automation.db')
        cursor = conn.cursor()
        
        # Insert blog data
        cursor.execute('''
            INSERT OR REPLACE INTO blogs (url, domain, category, analysis_metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            scraped_data['url'],
            scraped_data['url'].split('/')[2],  # Extract domain
            scraped_data.get('contentType', 'webpage'),
            json.dumps(scraped_data.get('metadata', {}))
        ))
        
        blog_id = cursor.lastrowid
        
        # Insert blog post data
        cursor.execute('''
            INSERT OR REPLACE INTO blog_posts (blog_id, url, title, content_summary, word_count, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            blog_id,
            scraped_data['url'],
            scraped_data.get('title', 'No title'),
            scraped_data.get('content', '')[:500],  # First 500 chars
            scraped_data.get('metadata', {}).get('wordCount', 0),
            'analyzed'
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Data inserted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database insertion failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting integration tests...\n")
    
    # Test 1: Database
    if not test_database():
        return
    print()
    
    # Test 2: Bun service
    scraped_data = test_bun_service()
    if not scraped_data:
        return
    print()
    
    # Test 3: Database insertion
    if not test_database_insertion(scraped_data['data']):
        return
    print()
    
    # Test 4: Verify insertion
    if not test_database():
        return
    
    print("🎉 All tests passed! Integration is working correctly!")

if __name__ == "__main__":
    main()
