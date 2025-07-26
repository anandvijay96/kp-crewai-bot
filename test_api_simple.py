#!/usr/bin/env python3
"""
Simple API Test - Health Check Only
===================================

Test if the FastAPI server can start without import errors.
"""

import sys
import os
import asyncio
import requests
import subprocess
import time
from threading import Thread

def test_api_startup():
    """Test if the API can start successfully."""
    print("🧪 Testing API startup...")
    
    # Start API server in a separate process
    api_process = None
    try:
        # Start the API server
        print("🚀 Starting API server...")
        api_process = subprocess.Popen([
            sys.executable, "-m", "src.api.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        print("⏳ Waiting for server to start...")
        time.sleep(10)
        
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Failed to reach health endpoint: {e}")
            return False
            
    except Exception as e:
        print(f"❌ API startup test failed: {e}")
        return False
    finally:
        if api_process:
            print("🛑 Stopping API server...")
            api_process.terminate()
            api_process.wait()
    
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 CrewAI KP Bot API - Simple Startup Test")
    print("=" * 50)
    
    success = test_api_startup()
    
    if success:
        print("\n🎉 API startup test PASSED!")
        print("✅ The API server can start and respond to health checks")
    else:
        print("\n❌ API startup test FAILED!")
        print("🔧 Check the logs above for import or startup issues")
    
    sys.exit(0 if success else 1)
