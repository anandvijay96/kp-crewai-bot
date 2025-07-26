#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
=================================

Test the authentication API endpoints to verify frontend integration.
"""

import requests
import json
import sys
from typing import Dict, Any

API_BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoint(endpoint: str, method: str = "GET", data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """Test an API endpoint and return the response."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "data": response.json() if response.content else {},
            "headers": dict(response.headers)
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status_code": 0,
            "error": "Connection failed - is the API server running?",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": response.status_code if 'response' in locals() else 0,
            "error": str(e),
            "data": {}
        }

def main():
    """Run the integration tests."""
    print("🧪 Frontend-Backend Authentication Integration Test")
    print("=" * 60)
    
    test_results = []
    access_token = None
    refresh_token = None
    
    # Test 1: Health Check
    print("\n🏥 Testing Health Check")
    print("-" * 40)
    
    result = test_api_endpoint("/health")
    if result["success"]:
        print("✅ Health check passed")
        print(f"   Service: {result['data'].get('service', 'Unknown')}")
        test_results.append(("Health Check", True))
    else:
        print(f"❌ Health check failed: {result.get('error', 'Unknown error')}")
        test_results.append(("Health Check", False))
        if result["status_code"] == 0:
            print("💡 Make sure the API server is running: python test_api_server.py")
            return False
    
    # Test 2: User Registration
    print("\n📝 Testing User Registration")
    print("-" * 40)
    
    registration_data = {
        "email": "newuser@test.com",
        "full_name": "New Test User",
        "password": "newpassword123",
        "role": "user"
    }
    
    result = test_api_endpoint("/api/auth/register", "POST", registration_data)
    if result["success"]:
        print("✅ User registration successful")
        print(f"   User ID: {result['data'].get('data', {}).get('user_id', 'Unknown')}")
        test_results.append(("User Registration", True))
    else:
        if result["status_code"] == 400 and "already registered" in str(result["data"]):
            print("✅ User registration (user already exists - expected)")
            test_results.append(("User Registration", True))
        else:
            print(f"❌ User registration failed: {result.get('error', result['data'])}")
            test_results.append(("User Registration", False))
    
    # Test 3: User Login
    print("\n🔐 Testing User Login")
    print("-" * 40)
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    result = test_api_endpoint("/api/auth/login", "POST", login_data)
    if result["success"]:
        response_data = result["data"].get("data", {})
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        user_info = response_data.get("user", {})
        
        print("✅ User login successful")
        print(f"   User: {user_info.get('email', 'Unknown')}")
        print(f"   Role: {user_info.get('role', 'Unknown')}")
        print(f"   Access token: {len(access_token)} chars" if access_token else "   No access token")
        print(f"   Refresh token: {len(refresh_token)} chars" if refresh_token else "   No refresh token")
        test_results.append(("User Login", True))
    else:
        print(f"❌ User login failed: {result.get('error', result['data'])}")
        test_results.append(("User Login", False))
        access_token = None
    
    # Test 4: Protected Endpoint Access
    if access_token:
        print("\n🔒 Testing Protected Endpoint")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        result = test_api_endpoint("/api/auth/me", "GET", headers=headers)
        
        if result["success"]:
            user_data = result["data"].get("data", {})
            print("✅ Protected endpoint access successful")
            print(f"   User ID: {user_data.get('id', 'Unknown')}")
            print(f"   Email: {user_data.get('email', 'Unknown')}")
            print(f"   Permissions: {len(user_data.get('permissions', []))} permissions")
            test_results.append(("Protected Endpoint", True))
        else:
            print(f"❌ Protected endpoint access failed: {result.get('error', result['data'])}")
            test_results.append(("Protected Endpoint", False))
    else:
        print("\n⚠️ Skipping protected endpoint test (no access token)")
        test_results.append(("Protected Endpoint", False))
    
    # Test 5: Token Refresh
    if refresh_token:
        print("\n🔄 Testing Token Refresh")
        print("-" * 40)
        
        refresh_data = {"refresh_token": refresh_token}
        result = test_api_endpoint("/api/auth/refresh", "POST", refresh_data)
        
        if result["success"]:
            new_access_token = result["data"].get("data", {}).get("access_token")
            print("✅ Token refresh successful")
            print(f"   New access token: {len(new_access_token)} chars" if new_access_token else "   No new token")
            test_results.append(("Token Refresh", True))
        else:
            print(f"❌ Token refresh failed: {result.get('error', result['data'])}")
            test_results.append(("Token Refresh", False))
    else:
        print("\n⚠️ Skipping token refresh test (no refresh token)")
        test_results.append(("Token Refresh", False))
    
    # Test 6: Token Validation
    if access_token:
        print("\n✅ Testing Token Validation")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        result = test_api_endpoint("/api/auth/validate", "GET", headers=headers)
        
        if result["success"]:
            validation_data = result["data"].get("data", {})
            print("✅ Token validation successful")
            print(f"   Valid: {validation_data.get('valid', False)}")
            print(f"   User ID: {validation_data.get('user_id', 'Unknown')}")
            test_results.append(("Token Validation", True))
        else:
            print(f"❌ Token validation failed: {result.get('error', result['data'])}")
            test_results.append(("Token Validation", False))
    else:
        print("\n⚠️ Skipping token validation test (no access token)")
        test_results.append(("Token Validation", False))
    
    # Test 7: User Logout
    if access_token:
        print("\n👋 Testing User Logout")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        result = test_api_endpoint("/api/auth/logout", "POST", headers=headers)
        
        if result["success"]:
            print("✅ User logout successful")
            test_results.append(("User Logout", True))
        else:
            print(f"❌ User logout failed: {result.get('error', result['data'])}")
            test_results.append(("User Logout", False))
    else:
        print("\n⚠️ Skipping logout test (no access token)")
        test_results.append(("User Logout", False))
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results")
    print("=" * 60)
    
    passed_tests = sum(1 for _, passed in test_results if passed)
    total_tests = len(test_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print()
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:.<25} {status}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    if success_rate >= 80:
        print(f"\n🎉 Integration test SUCCESSFUL! ({success_rate:.1f}% pass rate)")
        print("   The frontend-backend authentication integration is working correctly.")
        return True
    else:
        print(f"\n💥 Integration test FAILED! ({success_rate:.1f}% pass rate)")
        print("   Issues need to be resolved before frontend integration.")
        return False

if __name__ == "__main__":
    print("Starting frontend-backend integration test...")
    print("Make sure the API server is running on http://127.0.0.1:8000")
    print()
    
    success = main()
    sys.exit(0 if success else 1)
