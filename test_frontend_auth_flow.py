#!/usr/bin/env python3
"""
Frontend Authentication Flow Test
=================================

Test the exact authentication flow that the frontend API client uses.
"""

import requests
import json
import time
import sys

class FrontendSimulator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        # Simulate localStorage
        self.localStorage = {}
        
    def get_storage_item(self, key):
        return self.localStorage.get(key)
    
    def set_storage_item(self, key, value):
        self.localStorage[key] = value
        
    def remove_storage_item(self, key):
        self.localStorage.pop(key, None)
    
    def clear_auth_storage(self):
        """Clear all auth-related storage items."""
        auth_keys = [
            'kp_access_token',
            'kp_refresh_token', 
            'kp_token_expiry',
            'kp_user_data'
        ]
        for key in auth_keys:
            self.remove_storage_item(key)
            
    def is_token_expired(self):
        """Check if token is expired."""
        expiry_time = self.get_storage_item('kp_token_expiry')
        if not expiry_time:
            return True
        
        current_time = int(time.time() * 1000)  # Convert to milliseconds
        return current_time >= int(expiry_time)
    
    def get_access_token(self):
        """Get stored access token."""
        return self.get_storage_item('kp_access_token')
    
    def get_refresh_token(self):
        """Get stored refresh token."""
        return self.get_storage_item('kp_refresh_token')
    
    def refresh_token(self):
        """Attempt to refresh the access token."""
        refresh_token = self.get_refresh_token()
        if not refresh_token:
            raise Exception("No refresh token available")
        
        print(f"🔄 Attempting to refresh token...")
        
        response = self.session.post(
            f"{self.base_url}/api/auth/refresh",
            json={"refresh_token": refresh_token},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                token_data = data["data"]
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                
                if access_token:
                    expiry_time = int(time.time() * 1000) + (expires_in * 1000)
                    self.set_storage_item('kp_access_token', access_token)
                    self.set_storage_item('kp_token_expiry', str(expiry_time))
                    print("✅ Token refresh successful!")
                    return
        
        # If we get here, refresh failed
        print("❌ Token refresh failed, clearing auth data")
        self.clear_auth_storage()
        raise Exception("Token refresh failed")
    
    def make_authenticated_request(self, endpoint):
        """Make an authenticated request like the frontend does."""
        
        print(f"📡 Making authenticated request to: {endpoint}")
        
        # Check if token needs refresh
        if self.is_token_expired():
            print("⏰ Token is expired, attempting refresh...")
            try:
                self.refresh_token()
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                return None
        
        # Make the request with the token
        access_token = self.get_access_token()
        headers = {"Content-Type": "application/json"}
        
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            print(f"🎫 Using access token: {access_token[:20]}...")
        else:
            print("🚫 No access token available")
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 401:
                print("🔐 Got 401, trying token refresh...")
                try:
                    self.refresh_token()
                    # Retry with new token
                    new_token = self.get_access_token()
                    if new_token:
                        headers["Authorization"] = f"Bearer {new_token}"
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=30
                        )
                        print(f"📊 Retry Status Code: {response.status_code}")
                except Exception as e:
                    print(f"❌ Retry after refresh failed: {e}")
                    return None
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("❌ Failed to parse JSON response")
                    return None
            else:
                print(f"❌ Request failed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

def test_clean_slate():
    """Test with no stored tokens (clean slate)."""
    
    print("🧹 Testing Clean Slate (No Stored Tokens)")
    print("=" * 60)
    
    simulator = FrontendSimulator()
    result = simulator.make_authenticated_request("/api/dashboard/data")
    
    if result:
        print("✅ Clean slate test successful!")
        print(f"📄 Data received: {json.dumps(result, indent=2)}")
        return True
    else:
        print("❌ Clean slate test failed")
        return False

def test_with_expired_tokens():
    """Test with expired tokens stored."""
    
    print("\n⏰ Testing With Expired Tokens")
    print("=" * 60)
    
    simulator = FrontendSimulator()
    
    # Set up expired tokens
    simulator.set_storage_item('kp_access_token', 'expired_token_123')
    simulator.set_storage_item('kp_refresh_token', 'expired_refresh_123')
    simulator.set_storage_item('kp_token_expiry', str(int(time.time() * 1000) - 3600000))  # 1 hour ago
    
    print("🗃️  Set up expired tokens in localStorage simulation")
    
    result = simulator.make_authenticated_request("/api/dashboard/data")
    
    if result:
        print("✅ Expired tokens test successful!")
        return True
    else:
        print("❌ Expired tokens test failed")
        return False

def test_with_valid_tokens():
    """Test with valid tokens by first authenticating."""
    
    print("\n🔐 Testing With Valid Authentication")
    print("=" * 60)
    
    simulator = FrontendSimulator()
    
    # First, authenticate to get valid tokens
    print("🔑 Step 1: Authenticating to get valid tokens...")
    
    # Register a test user first
    register_response = simulator.session.post(
        f"{simulator.base_url}/api/auth/register",
        json={
            "email": "frontend_test@example.com",
            "password": "testpass123",
            "full_name": "Frontend Test User"
        },
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Try to login
    login_response = simulator.session.post(
        f"{simulator.base_url}/api/auth/login",
        json={
            "email": "frontend_test@example.com",
            "password": "testpass123"
        },
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        if login_data.get("success") and "data" in login_data:
            token_data = login_data["data"]
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            
            if access_token and refresh_token:
                # Store tokens
                expiry_time = int(time.time() * 1000) + (expires_in * 1000)
                simulator.set_storage_item('kp_access_token', access_token)
                simulator.set_storage_item('kp_refresh_token', refresh_token)
                simulator.set_storage_item('kp_token_expiry', str(expiry_time))
                
                print("✅ Authentication successful, tokens stored")
                
                # Now test the dashboard request
                print("🔑 Step 2: Making dashboard request with valid tokens...")
                result = simulator.make_authenticated_request("/api/dashboard/data")
                
                if result:
                    print("✅ Valid tokens test successful!")
                    return True
    
    print("❌ Valid tokens test failed")
    return False

if __name__ == "__main__":
    print("🚀 CrewAI KP Bot - Frontend Authentication Flow Test")
    print("==================================================")
    
    # Test different scenarios
    clean_slate_works = test_clean_slate()
    expired_tokens_works = test_with_expired_tokens() 
    valid_tokens_works = test_with_valid_tokens()
    
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"Clean Slate (No Tokens): {'✅ PASS' if clean_slate_works else '❌ FAIL'}")
    print(f"Expired Tokens: {'✅ PASS' if expired_tokens_works else '❌ FAIL'}")
    print(f"Valid Tokens: {'✅ PASS' if valid_tokens_works else '❌ FAIL'}")
    
    if clean_slate_works:
        print("\n🎉 Great! The dashboard should work without authentication.")
        print("💡 If the frontend is still having issues, the problem is likely:")
        print("   1. Old tokens in browser localStorage causing auth failures")
        print("   2. JavaScript errors in the browser console")
        print("   3. Network connectivity issues between frontend and backend")
        print("   4. Browser cache issues")
        print("\n🔧 Quick Fix: Clear browser localStorage by opening DevTools and running:")
        print("   localStorage.clear()")
    
    elif valid_tokens_works:
        print("\n🎉 Authentication flow works when tokens are valid.")
        print("💡 The issue might be old/corrupted tokens in localStorage.")
    
    else:
        print("\n🔧 Authentication flow has issues that need fixing.")
    
    sys.exit(0 if (clean_slate_works or valid_tokens_works) else 1)
