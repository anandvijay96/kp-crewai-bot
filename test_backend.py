#!/usr/bin/env python3
"""
Backend Server Test Script
=========================

Quick test to verify the backend server is running and authentication endpoints are accessible.
"""

import requests
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running!")
            print(f"   Health check response: {response.json()}")
            return True
        else:
            print(f"❌ Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print(f"   Make sure the server is running on {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    try:
        test_user = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPassword123",
            "role": "user"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json=test_user,
            timeout=10
        )
        
        print(f"\n📝 Registration test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration endpoint is working!")
            print(f"   Response: {response.json()}")
            return True
        elif response.status_code == 400:
            # User might already exist
            print("ℹ️  Registration endpoint is accessible (user may already exist)")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return False

def test_user_login():
    """Test user login endpoint"""
    try:
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"\n🔑 Login test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login endpoint is working!")
            data = response.json()
            if 'data' in data and 'access_token' in data['data']:
                print("✅ JWT tokens are being generated correctly!")
                return data['data']['access_token']
            else:
                print("⚠️  Login successful but token format unexpected")
                print(f"   Response: {data}")
                return None
        elif response.status_code == 401:
            print("ℹ️  Login endpoint is accessible (credentials may be invalid)")
            print(f"   Response: {response.json()}")
            return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_protected_endpoint(access_token: str):
    """Test a protected endpoint with JWT token"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers=headers,
            timeout=10
        )
        
        print(f"\n🔒 Protected endpoint test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoints are working!")
            print(f"   User data: {response.json()}")
            return True
        else:
            print(f"❌ Protected endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing protected endpoint: {e}")
        return False

def main():
    """Run all backend tests"""
    print("🚀 Testing CrewAI KP Bot Backend Authentication")
    print("=" * 50)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend server is not running. Please start it first.")
        print("   Run: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Registration
    test_user_registration()
    
    # Test 3: Login
    access_token = test_user_login()
    
    # Test 4: Protected endpoint (if we have a token)
    if access_token:
        test_protected_endpoint(access_token)
    
    print("\n" + "=" * 50)
    print("🎉 Backend authentication testing complete!")

if __name__ == "__main__":
    main()
