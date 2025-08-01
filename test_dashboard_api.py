#!/usr/bin/env python3
"""
Dashboard API Test Script
========================

Test script to verify the dashboard API endpoint is working correctly.
"""

import requests
import json
import sys

def test_dashboard_endpoint():
    """Test the dashboard endpoint without authentication."""
    
    print("🧪 Testing Dashboard API Endpoint")
    print("=" * 50)
    
    # Test the dashboard endpoint
    url = "http://localhost:8000/api/dashboard/data"
    
    try:
        print(f"📡 Making request to: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard endpoint successful!")
            print("📄 Response data:")
            print(json.dumps(data, indent=2))
            
            # Check if it matches expected structure
            if "success" in data and "data" in data:
                dashboard_data = data["data"]
                required_fields = [
                    "activeCampaigns", "blogsDiscovered", 
                    "commentsGenerated", "successRate",
                    "recentCampaigns", "topBlogs"
                ]
                
                missing_fields = [field for field in required_fields if field not in dashboard_data]
                
                if not missing_fields:
                    print("✅ All required fields present in dashboard data!")
                    return True
                else:
                    print(f"❌ Missing fields: {missing_fields}")
                    return False
            else:
                print("❌ Response doesn't match expected API structure")
                return False
        else:
            print(f"❌ Dashboard endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_with_authentication():
    """Test with authentication if possible."""
    
    print("\n🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # First try to register a test user
    register_url = "http://localhost:8000/api/auth/register"
    register_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        print("📝 Attempting to register test user...")
        register_response = requests.post(
            register_url, 
            json=register_data, 
            timeout=10
        )
        
        if register_response.status_code == 201:
            print("✅ User registration successful!")
        elif register_response.status_code == 400:
            print("ℹ️  User may already exist, trying login...")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            try:
                print(f"Error: {register_response.json()}")
            except:
                print(f"Error text: {register_response.text}")
    
    except Exception as e:
        print(f"❌ Registration request failed: {e}")
    
    # Try to login
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        print("🔑 Attempting to login...")
        login_response = requests.post(
            login_url,
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login successful!")
            
            if "data" in login_result and "access_token" in login_result["data"]:
                access_token = login_result["data"]["access_token"]
                print("🎫 Got access token, testing authenticated dashboard...")
                
                # Test dashboard with authentication
                headers = {"Authorization": f"Bearer {access_token}"}
                dashboard_response = requests.get(
                    "http://localhost:8000/api/dashboard/data",
                    headers=headers,
                    timeout=10
                )
                
                if dashboard_response.status_code == 200:
                    print("✅ Authenticated dashboard request successful!")
                    return True
                else:
                    print(f"❌ Authenticated dashboard failed: {dashboard_response.status_code}")
            else:
                print("❌ Login response missing access token")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            try:
                print(f"Error: {login_response.json()}")
            except:
                print(f"Error text: {login_response.text}")
    
    except Exception as e:
        print(f"❌ Login request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 CrewAI KP Bot - Dashboard API Test")
    print("====================================")
    
    # Test basic dashboard endpoint
    dashboard_works = test_dashboard_endpoint()
    
    # Test authentication flow
    auth_works = test_with_authentication()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Dashboard Endpoint: {'✅ PASS' if dashboard_works else '❌ FAIL'}")
    print(f"Authentication Flow: {'✅ PASS' if auth_works else '❌ FAIL'}")
    
    if dashboard_works:
        print("\n🎉 Dashboard should work in the frontend!")
    else:
        print("\n🔧 Dashboard needs fixing before frontend will work properly.")
    
    sys.exit(0 if dashboard_works else 1)
