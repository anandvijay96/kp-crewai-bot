#!/usr/bin/env python3
"""
Frontend Simulation Test
========================

Simulate exactly what the frontend does to debug the dashboard loading issue.
"""

import requests
import json
import sys

def simulate_frontend_request():
    """Simulate the exact request the frontend makes."""
    
    print("🌐 Simulating Frontend Dashboard Request")
    print("=" * 50)
    
    # This is what the frontend apiClient does
    api_base_url = "http://localhost:8000"
    endpoint = "/api/dashboard/data"
    full_url = f"{api_base_url}{endpoint}"
    
    # Headers that frontend would send
    headers = {
        "Content-Type": "application/json",
        # No Authorization header initially (frontend will get 401 and try to refresh)
    }
    
    try:
        print(f"📡 Making request to: {full_url}")
        print(f"📋 Headers: {headers}")
        
        response = requests.get(full_url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Request successful!")
                print("📄 Response data:")
                print(json.dumps(data, indent=2))
                
                # Check if it matches ApiResponse<DashboardData> structure
                if isinstance(data, dict) and "success" in data:
                    if data.get("success") and "data" in data:
                        dashboard_data = data["data"]
                        print("✅ Response matches expected ApiResponse structure!")
                        
                        # Verify dashboard data structure
                        required_fields = [
                            "activeCampaigns", "blogsDiscovered", 
                            "commentsGenerated", "successRate",
                            "recentCampaigns", "topBlogs"
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in dashboard_data]
                        
                        if not missing_fields:
                            print("✅ Dashboard data has all required fields!")
                            print("📊 Dashboard Data Summary:")
                            print(f"   - Active Campaigns: {dashboard_data.get('activeCampaigns')}")
                            print(f"   - Blogs Discovered: {dashboard_data.get('blogsDiscovered')}")
                            print(f"   - Comments Generated: {dashboard_data.get('commentsGenerated')}")
                            print(f"   - Success Rate: {dashboard_data.get('successRate')}%")
                            print(f"   - Recent Campaigns: {len(dashboard_data.get('recentCampaigns', []))}")
                            print(f"   - Top Blogs: {len(dashboard_data.get('topBlogs', []))}")
                            return True
                        else:
                            print(f"❌ Missing fields in dashboard data: {missing_fields}")
                            return False
                    else:
                        print(f"❌ API returned success=False: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    print("❌ Response doesn't match expected ApiResponse structure")
                    print("Expected: { success: boolean, message: string, data: {...} }")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return False
                
        elif response.status_code == 401:
            print("🔐 Got 401 Unauthorized - this is expected behavior")
            print("Frontend should handle this by trying to refresh token or redirect to login")
            
            # Check if there's a meaningful error message
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
                
            return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30 seconds)")
        print("This suggests the backend server might not be running or is unresponsive")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - cannot reach the server")
        print("Please verify the backend server is running on http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request."""
    
    print("\n🌐 Testing CORS Preflight Request")
    print("=" * 50)
    
    url = "http://localhost:8000/api/dashboard/data"
    
    # Simulate preflight OPTIONS request
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "content-type,authorization"
    }
    
    try:
        print(f"📡 Making OPTIONS request to: {url}")
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 204]:
            cors_headers = {
                k: v for k, v in response.headers.items() 
                if k.lower().startswith('access-control-')
            }
            
            if cors_headers:
                print("✅ CORS headers present:")
                for k, v in cors_headers.items():
                    print(f"   {k}: {v}")
                return True
            else:
                print("❌ No CORS headers in response")
                return False
        else:
            print(f"❌ OPTIONS request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CORS preflight test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CrewAI KP Bot - Frontend Simulation Test")
    print("==========================================")
    
    # Test the main request
    main_request_works = simulate_frontend_request()
    
    # Test CORS
    cors_works = test_cors_preflight()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Main Request: {'✅ PASS' if main_request_works else '❌ FAIL'}")
    print(f"CORS Preflight: {'✅ PASS' if cors_works else '❌ FAIL'}")
    
    if main_request_works:
        print("\n🎉 The dashboard API should work perfectly in the frontend!")
        print("If the frontend is still showing 'Loading...' or an error:")
        print("1. Check browser console for any JavaScript errors")
        print("2. Check browser Network tab to see actual requests")
        print("3. Verify the frontend is running on port 3000")
        print("4. Clear browser cache and localStorage")
    else:
        print("\n🔧 Issues found that need to be fixed:")
        if not main_request_works:
            print("- Dashboard API request is failing")
        if not cors_works:
            print("- CORS configuration may have issues")
    
    sys.exit(0 if main_request_works else 1)
