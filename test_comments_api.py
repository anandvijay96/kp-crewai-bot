#!/usr/bin/env python3
"""
Test script to verify comments API endpoints work correctly
"""

import requests
import json

def test_comments_api():
    # First login to get a token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    credentials = {
        "email": "demo@test.com",
        "password": "demo123"
    }
    
    print("🔐 Testing login...")
    login_response = requests.post(login_url, json=credentials)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return None
    
    login_data = login_response.json()
    token = login_data['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Test comments health endpoint
    print("\n🏥 Testing comments health endpoint...")
    health_url = "http://127.0.0.1:8000/api/comments/health"
    
    try:
        health_response = requests.get(health_url)
        print(f"📊 Health Status Code: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Comments health check successful!")
            print(f"Service: {health_data.get('service', 'Unknown')}")
            print(f"Status: {health_data.get('status', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {health_response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test comments list endpoint
    print("\n📝 Testing comments list endpoint...")
    list_url = "http://127.0.0.1:8000/api/comments/"
    
    try:
        list_response = requests.get(list_url, headers=headers)
        print(f"📊 List Status Code: {list_response.status_code}")
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            print("✅ Comments list successful!")
            print(f"Message: {list_data.get('message', 'No message')}")
            comments = list_data.get('comments', [])
            print(f"Comments found: {len(comments)}")
            if comments:
                for i, comment in enumerate(comments[:2]):  # Show first 2
                    print(f"  Comment {i+1}: {comment.get('content', 'No content')[:50]}...")
        else:
            print(f"❌ Comments list failed: {list_response.text}")
    except Exception as e:
        print(f"❌ Comments list error: {e}")
    
    # Test comment generation
    print("\n🤖 Testing comment generation...")
    generate_url = "http://127.0.0.1:8000/api/comments/generate"
    
    generation_request = {
        "blog_url": "https://example.com/test-blog",
        "style": "engaging",
        "max_comments": 2,
        "keywords": ["SEO", "optimization"]
    }
    
    try:
        generate_response = requests.post(generate_url, json=generation_request, headers=headers)
        print(f"📊 Generation Status Code: {generate_response.status_code}")
        
        if generate_response.status_code == 200:
            generate_data = generate_response.json()
            print("✅ Comment generation successful!")
            print(f"Message: {generate_data.get('message', 'No message')}")
            comments = generate_data.get('comments', [])
            print(f"Generated comments: {len(comments)}")
            if comments:
                for i, comment in enumerate(comments):
                    print(f"  Generated Comment {i+1}: {comment.get('content', 'No content')[:70]}...")
        else:
            print(f"❌ Comment generation failed: {generate_response.text}")
    except Exception as e:
        print(f"❌ Comment generation error: {e}")
    
    # Test comments list again to see if new comments appear
    print("\n🔄 Testing comments list after generation...")
    
    try:
        list_response2 = requests.get(list_url, headers=headers)
        print(f"📊 List Status Code: {list_response2.status_code}")
        
        if list_response2.status_code == 200:
            list_data2 = list_response2.json()
            print("✅ Comments list after generation successful!")
            comments2 = list_data2.get('comments', [])
            print(f"Total comments now: {len(comments2)}")
            if comments2:
                print("Recent comments:")
                for i, comment in enumerate(comments2[:3]):  # Show first 3
                    print(f"  Comment {i+1}: {comment.get('content', 'No content')[:50]}...")
        else:
            print(f"❌ Comments list after generation failed: {list_response2.text}")
    except Exception as e:
        print(f"❌ Comments list after generation error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Comments API...")
    print("=" * 60)
    
    test_comments_api()
    
    print("\n" + "=" * 60)
    print("✨ Comments API test complete!")
