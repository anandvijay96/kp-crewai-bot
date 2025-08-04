#!/usr/bin/env python3
"""
Simple test script to verify login API endpoint works
"""

import requests
import json

def test_login():
    # Test credentials
    credentials = {
        "email": "demo@test.com",
        "password": "demo123"
    }
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/auth/login"
    
    print(f"🔐 Testing login with: {credentials['email']}")
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.post(url, json=credentials)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"📝 Response: {json.dumps(data, indent=2)}")
            
            if data.get("success") and data.get("data", {}).get("access_token"):
                print(f"🔑 Access Token: {data['data']['access_token'][:50]}...")
                print(f"👤 User: {data['data']['user']['email']}")
                return data['data']['access_token']
            else:
                print("❌ Login response missing token")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend server running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_dashboard_with_token(token):
    """Test dashboard API with authentication token"""
    url = "http://127.0.0.1:8000/api/dashboard/data"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Testing dashboard API with token...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard API successful!")
            print(f"📈 Blogs Discovered: {data.get('blogsDiscovered', 'N/A')}")
            print(f"💬 Comments Generated: {data.get('commentsGenerated', 'N/A')}")
            print(f"🎯 Success Rate: {data.get('successRate', 'N/A')}%")
        else:
            print(f"❌ Dashboard API failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Dashboard API error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Login API...")
    print("=" * 50)
    
    token = test_login()
    
    if token:
        test_dashboard_with_token(token)
    
    print("\n" + "=" * 50)
    print("✨ Test complete!")
