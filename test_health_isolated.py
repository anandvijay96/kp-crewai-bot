#!/usr/bin/env python3
"""
Isolated Health Check Test
==========================

Test the health check endpoint in isolation.
"""

import sys
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_health_direct():
    """Test health endpoint directly without authentication."""
    print("🏥 Testing Health Check Endpoint Directly")
    print("=" * 60)
    
    try:
        # Create a minimal FastAPI app
        app = FastAPI(title="Health Test")
        
        # Define the health check endpoint directly
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "Test Service",
                "features": ["Feature 1", "Feature 2"],
                "endpoints": {"test": "GET /test"}
            }
        
        # Test with TestClient
        client = TestClient(app)
        response = client.get("/health")
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Direct health check works!")
            return True
        else:
            print("❌ Direct health check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_imported_health():
    """Test the imported health endpoint."""
    print("\n🏥 Testing Imported Health Check Endpoint")
    print("=" * 60)
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Try importing just the health check function
        from api.routes.blogs import blogs_health_check
        
        app = FastAPI()
        
        # Register the health check endpoint manually
        app.get("/api/blogs/health")(blogs_health_check)
        
        client = TestClient(app)
        
        # List routes
        print("Routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"  - {route.path}")
        
        response = client.get("/api/blogs/health")
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Imported health check works!")
            print(f"Service: {data.get('service', 'N/A')}")
            print(f"Status: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Imported health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_router_health():
    """Test health endpoint with full router."""
    print("\n🏥 Testing Router Health Check")
    print("=" * 60)
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Import without agent issues
        import logging
        logger = logging.getLogger(__name__)
        
        # Import the router
        from api.routes import blogs
        
        app = FastAPI()
        
        # Include the router without authentication override
        app.include_router(blogs.router, prefix="/api/blogs")
        
        client = TestClient(app)
        
        # Direct call to health endpoint
        response = client.get("/api/blogs/health")
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Router health check works!")
            return True
        elif response.status_code == 403:
            print("⚠️ Health check requires authentication")
            # Try with mock auth
            headers = {"Authorization": "Bearer mock-token"}
            response = client.get("/api/blogs/health", headers=headers)
            print(f"With auth header: {response.status_code}")
            return False
        else:
            print(f"❌ Router health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Running Isolated Health Check Tests")
    print("=" * 70)
    
    tests = [
        ("Direct health check", test_health_direct),
        ("Imported health check", test_imported_health),
        ("Router health check", test_router_health)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {name} passed")
        else:
            print(f"❌ {name} failed")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed > 0:
        print("✅ At least one health check method works!")
    else:
        print("❌ All health check methods failed!")
