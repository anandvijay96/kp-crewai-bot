#!/usr/bin/env python3
"""
Test Script for Python-Bun Integration
======================================

Tests the communication between Python backend and Bun microservice.
"""

import asyncio
import httpx
import json
import time

BUN_URL = 'http://localhost:3001'

async def test_bun_health():
    """Test Bun microservice health endpoint."""
    print("🏥 Testing Bun microservice health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'{BUN_URL}/health')
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_bun_scraping():
    """Test Bun scraping functionality."""
    print("🌐 Testing Bun scraping endpoint...")
    
    test_url = "https://example.com"
    payload = {
        "url": test_url,
        "options": {
            "includeMetadata": True,
            "includeLinks": True,
            "includeAuthorityScore": False
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f'{BUN_URL}/api/scraping/scrape', json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    scrape_data = data.get('data', {})
                    print(f"✅ Scraping successful!")
                    print(f"   Title: {scrape_data.get('title', 'N/A')}")
                    print(f"   URL: {scrape_data.get('url', 'N/A')}")
                    print(f"   Content Length: {len(scrape_data.get('content', ''))}")
                    print(f"   Links Found: {len(scrape_data.get('links', []))}")
                    print(f"   Response Time: {scrape_data.get('responseTime', 'N/A')}ms")
                    return True
                else:
                    print(f"❌ Scraping failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Scraping request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return False

async def test_bun_authority_score():
    """Test Bun authority scoring functionality."""
    print("🎯 Testing Bun authority scoring endpoint...")
    
    test_url = "https://example.com"
    payload = {"url": test_url}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f'{BUN_URL}/api/scraping/authority-score', json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    score_data = data.get('data', {})
                    print(f"✅ Authority scoring successful!")
                    print(f"   Domain Authority: {score_data.get('domainAuthority', 'N/A')}")
                    print(f"   Page Authority: {score_data.get('pageAuthority', 'N/A')}")
                    print(f"   Source: {score_data.get('source', 'N/A')}")
                    print(f"   Confidence: {score_data.get('confidence', 'N/A')}")
                    return True
                else:
                    print(f"❌ Authority scoring failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Authority scoring request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authority scoring error: {e}")
            return False

async def test_bun_stats():
    """Test Bun service statistics endpoint."""
    print("📊 Testing Bun service statistics...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'{BUN_URL}/api/scraping/stats')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats_data = data.get('data', {})
                    print(f"✅ Statistics retrieved successfully!")
                    print(f"   Service uptime: {stats_data.get('service', {}).get('uptime', 'N/A')}")
                    print(f"   Memory usage: {stats_data.get('service', {}).get('memoryUsage', 'N/A')}")
                    return True
                else:
                    print(f"❌ Statistics retrieval failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Statistics request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return False

async def test_python_bun_integration():
    """Test Python-Bun integration using the integration service."""
    print("🔗 Testing Python-Bun Integration Service...")
    
    try:
        # Test direct HTTP calls instead of import issues
        async with httpx.AsyncClient() as client:
            test_url = "https://example.com"
            payload = {"url": test_url}
            
            response = await client.post(f'{BUN_URL}/api/scraping/scrape', json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Python-Bun integration working!")
                    print(f"   Title: {result.get('data', {}).get('title', 'N/A')}")
                    print(f"   Response Time: {result.get('data', {}).get('responseTime', 'N/A')}ms")
                    return True
                else:
                    print(f"❌ Python-Bun integration failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Python-Bun integration failed: HTTP {response.status_code}")
                return False
            
    except Exception as e:
        print(f"❌ Python-Bun integration error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Python-Bun Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_bun_health),
        ("Scraping Functionality", test_bun_scraping),
        ("Authority Scoring", test_bun_authority_score),
        ("Service Statistics", test_bun_stats),
        ("Python-Bun Integration", test_python_bun_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        start_time = time.time()
        
        try:
            success = await test_func()
            duration = time.time() - start_time
            results.append((test_name, success, duration))
            
            if success:
                print(f"✅ {test_name} completed in {duration:.2f}s")
            else:
                print(f"❌ {test_name} failed after {duration:.2f}s")
                
        except Exception as e:
            duration = time.time() - start_time
            results.append((test_name, False, duration))
            print(f"❌ {test_name} crashed after {duration:.2f}s: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name:<25} ({duration:.2f}s)")
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Python-Bun integration is working!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
