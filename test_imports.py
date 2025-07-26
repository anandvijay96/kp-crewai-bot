#!/usr/bin/env python3
"""
Test Imports - API Components
=============================

Test if all API components can be imported without errors.
"""

import sys
import os

print("🧪 Testing API imports...")

try:
    print("📦 Testing core FastAPI imports...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
    
    from pydantic import BaseModel
    print("✅ Pydantic imported successfully")
    
except ImportError as e:
    print(f"❌ Core imports failed: {e}")
    sys.exit(1)

try:
    print("📦 Testing API models...")
    from src.api.models import BaseResponse, CampaignStatus
    print("✅ API models imported successfully")
    
except ImportError as e:
    print(f"❌ API models import failed: {e}")

try:
    print("📦 Testing auth module...")
    from src.api.auth import get_current_user
    print("✅ Auth module imported successfully")
    
except ImportError as e:
    print(f"❌ Auth module import failed: {e}")

try:
    print("📦 Testing websocket module...")
    from src.api.websocket import websocket_manager
    print("✅ WebSocket module imported successfully")
    
except ImportError as e:
    print(f"❌ WebSocket module import failed: {e}")

try:
    print("📦 Testing route modules...")
    from src.api.routes import campaigns, agents, blogs, comments, auth as auth_routes
    print("✅ Route modules imported successfully")
    
except ImportError as e:
    print(f"❌ Route modules import failed: {e}")

print("\n🎉 Import test completed!")
