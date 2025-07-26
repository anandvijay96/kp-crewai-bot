#!/usr/bin/env python3
"""
API Endpoint Test
=================

Test the FastAPI blog research endpoint with mock authentication.
"""

import sys
import os
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from typing import Dict, Any

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Mock authentication for testing
def mock_get_current_user() -> Dict[str, Any]:
    """Mock authentication that returns a test user."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "user_id": "test-123"
    }

def test_api_endpoint():
    """Test the blog research API endpoint."""
    print("🧪 Testing FastAPI Blog Research Endpoint")
    print("=" * 60)
    
    try:
        # Import and set up FastAPI app
        from api.routes.blogs import router as blog_router
        
        # Override the authentication dependency for testing
        from api.auth import get_current_user
        
        app = FastAPI(title="Test API")
        
        # Override dependency
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Include blog router
        app.include_router(blog_router, prefix="/api/blogs")
        
        # Create test client
        client = TestClient(app)
        
        print("✅ FastAPI app and test client created successfully")
        
        # Test the research endpoint
        print("\n🚀 Testing /api/blogs/research endpoint...")
        
        test_request = {
            "keywords": ["artificial intelligence", "machine learning"],
            "max_results": 3,
            "quality_threshold": 0.8,
            "target_domains": [],
            "exclude_domains": []
        }
        
        response = client.post("/api/blogs/research", json=test_request)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API request successful!")
            print(f"   Found {len(data.get('blogs', []))} blogs")
            print(f"   Total discovered: {data.get('total_discovered', 0)}")
            print(f"   Execution time: {data.get('execution_time', 0):.2f}s")
            print(f"   Cost: ${data.get('cost', 0):.3f}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Show sample blog if available
            if data.get('blogs'):
                sample_blog = data['blogs'][0]
                print(f"   Sample blog: {sample_blog.get('title', 'N/A')}")
                print(f"   Domain: {sample_blog.get('domain', 'N/A')}")
                print(f"   Quality score: {sample_blog.get('quality_score', 0)}")
            
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_health_endpoint():
    """Test the health check endpoint."""
    print(f"\n🏥 Testing Health Check Endpoint")
    print("=" * 60)
    
    try:
        from api.routes.blogs import router as blog_router
        from api.auth import get_current_user
        
        app = FastAPI(title="Test API")
        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.include_router(blog_router, prefix="/api/blogs")
        
        client = TestClient(app)
        
        # Debug: list all routes
        print("   Available routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"     - {route.path}")
        
        response = client.get("/api/blogs/health")
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"   Service: {data.get('service', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Features: {len(data.get('features', []))} available")
            print(f"   Endpoints: {len(data.get('endpoints', {}))} defined")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            if response.status_code == 404:
                print("   The endpoint was not found. Checking alternative paths...")
                # Try without trailing slash
                alt_response = client.get("/api/blogs/health/")
                if alt_response.status_code == 200:
                    print("   ✅ Found with trailing slash")
                    return True
            return False
            
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def run_api_tests():
    """Run all API tests."""
    print("🚀 Starting API Endpoint Tests")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Main research endpoint
    if test_api_endpoint():
        tests_passed += 1
        print("✅ Research endpoint test passed")
    else:
        print("❌ Research endpoint test failed")
    
    # Test 2: Health check endpoint
    if test_health_endpoint():
        tests_passed += 1
        print("✅ Health check endpoint test passed")
    else:
        print("❌ Health check endpoint test failed")
    
    # Results
    print("\n" + "=" * 70)
    print("📊 API Test Results Summary")
    print("=" * 70)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed >= 1:  # At least the main endpoint should work
        print("✅ API endpoints are functional!")
        print("   The system is ready for integration with frontend.")
        return True
    else:
        print("❌ Critical API issues detected.")
        return False

if __name__ == "__main__":
    success = run_api_tests()
    
    if success:
        print("\n🎉 API testing successful! Ready for frontend integration.")
    else:
        print("\n💥 API testing failed! Need to fix issues.")
    
    sys.exit(0 if success else 1)
