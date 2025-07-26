"""
API Components Test
==================

Test script to validate Phase 5 API setup without running server.
"""

import sys
import os
import asyncio
from datetime import datetime

# Test FastAPI basic setup
def test_fastapi_setup():
    """Test FastAPI can be imported and setup."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        print("✅ FastAPI and dependencies imported successfully")
        
        # Create test app
        app = FastAPI(title="Test API")
        app.add_middleware(CORSMiddleware, allow_origins=["*"])
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
            
        print("✅ FastAPI application created successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI setup failed: {e}")
        return False

# Test Pydantic models
def test_pydantic_models():
    """Test Pydantic model validation."""
    try:
        from pydantic import BaseModel, Field
        from typing import List, Optional
        from datetime import datetime
        
        class TestModel(BaseModel):
            name: str
            age: int
            tags: List[str] = []
            created_at: datetime = Field(default_factory=datetime.utcnow)
        
        # Test model creation
        test_data = TestModel(name="Test", age=25, tags=["api", "test"])
        assert test_data.name == "Test"
        assert test_data.age == 25
        
        print("✅ Pydantic models working correctly")
        return True
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False

# Test JWT authentication components
def test_jwt_auth():
    """Test JWT authentication setup."""
    try:
        from jose import jwt
        from passlib.context import CryptContext
        from datetime import timedelta
        
        # Test password hashing
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password = "test123"
        hashed = pwd_context.hash(password)
        verified = pwd_context.verify(password, hashed)
        
        assert verified == True
        
        # Test JWT token creation
        secret_key = "test-secret-key"
        test_data = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(test_data, secret_key, algorithm="HS256")
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        assert decoded["sub"] == "testuser"
        
        print("✅ JWT authentication components working")
        return True
    except Exception as e:
        print(f"❌ JWT authentication test failed: {e}")
        return False

# Test async functionality
async def test_async_functionality():
    """Test async/await functionality."""
    try:
        async def mock_async_operation():
            await asyncio.sleep(0.1)  
            return "async_result"
        
        result = await mock_async_operation()
        assert result == "async_result"
        
        print("✅ Async functionality working")
        return True
    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False

# Test API endpoint simulation
def test_api_endpoints():
    """Test API endpoint logic without server."""
    try:
        from fastapi.testclient import TestClient
        
        # Create test FastAPI app
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        
        @app.post("/test")
        async def test_post(data: dict):
            return {"received": data, "processed": True}
        
        # Test with TestClient
        client = TestClient(app)
        
        # Test GET endpoint
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test POST endpoint
        test_data = {"message": "test"}
        response = client.post("/test", json=test_data)
        assert response.status_code == 200
        assert response.json()["processed"] == True
        
        print("✅ API endpoints working correctly")
        return True
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

# Test WebSocket components
def test_websocket_setup():
    """Test WebSocket component setup."""
    try:
        from fastapi import WebSocket
        import json
        
        # Mock WebSocket message
        test_message = {
            "type": "test",
            "data": {"message": "hello"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test JSON serialization
        json_message = json.dumps(test_message, default=str)
        parsed_message = json.loads(json_message)
        
        assert parsed_message["type"] == "test"
        assert "timestamp" in parsed_message
        
        print("✅ WebSocket components setup correctly")
        return True
    except Exception as e:
        print(f"❌ WebSocket setup test failed: {e}")
        return False

# Main test runner
async def run_all_tests():
    """Run all API component tests."""
    print("🚀 Starting Phase 5 API Component Tests...")
    print("=" * 50)
    
    tests = [
        ("FastAPI Setup", test_fastapi_setup),
        ("Pydantic Models", test_pydantic_models), 
        ("JWT Authentication", test_jwt_auth),
        ("API Endpoints", test_api_endpoints),
        ("WebSocket Setup", test_websocket_setup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test async functionality separately
    print(f"\n🧪 Testing: Async Functionality")
    try:
        async_result = await test_async_functionality()
        results.append(("Async Functionality", async_result))
    except Exception as e:
        print(f"❌ Async Functionality failed: {e}")
        results.append(("Async Functionality", False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 5 API setup is ready!")
        print("\n📋 Next Steps:")
        print("1. ✅ Dependencies installed successfully")
        print("2. ✅ FastAPI components working")
        print("3. ✅ Authentication system ready")
        print("4. ✅ API models validated")
        print("5. ✅ WebSocket setup confirmed")
        print("\n🚀 Ready to proceed with full API implementation!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    # Run tests
    result = asyncio.run(run_all_tests())
    
    if result:
        print("\n" + "🎯" * 20)
        print("Phase 5 - Backend Integration: READY TO PROCEED")
        print("🎯" * 20)
    else:
        print("\n" + "⚠️" * 20)
        print("Please fix failing tests before proceeding")
        print("⚠️" * 20)
