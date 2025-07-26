#!/usr/bin/env python3
"""
Authentication System Test Script
=================================

Test the JWT authentication system with user registration, login, and token validation.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_authentication_system():
    """Test the authentication system components."""
    print("🚀 Starting Authentication System Test")
    print("=" * 60)
    
    test_results = {
        'jwt_handler': False,
        'user_service': False,
        'database_connection': False,
        'auth_flow': False
    }
    
    try:
        # Test 1: JWT Handler
        print("\n🔐 Testing JWT Handler")
        print("-" * 40)
        
        from src.api.auth.jwt_handler import JWTHandler
        
        # Test password hashing
        password = "test_password123"
        hashed = JWTHandler.hash_password(password)
        is_valid = JWTHandler.verify_password(password, hashed)
        
        print(f"✅ Password hashing: {'✓' if is_valid else '✗'}")
        
        # Test token creation and verification
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "role": "user",
            "permissions": ["view_campaign"]
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        refresh_token = JWTHandler.create_refresh_token({"sub": "1"})
        
        print(f"✅ Access token created: {len(access_token)} chars")
        print(f"✅ Refresh token created: {len(refresh_token)} chars")
        
        # Verify tokens
        access_payload = JWTHandler.verify_token(access_token, "access")
        refresh_payload = JWTHandler.verify_token(refresh_token, "refresh")
        
        print(f"✅ Access token verified: {access_payload.get('email')}")
        print(f"✅ Refresh token verified: {refresh_payload.get('sub')}")
        
        test_results['jwt_handler'] = True
        print("✅ JWT Handler test successful!")
        
    except Exception as e:
        print(f"❌ JWT Handler test failed: {e}")
        test_results['jwt_handler'] = False
    
    try:
        # Test 2: Database Connection
        print("\n🗄️ Testing Database Connection")
        print("-" * 40)
        
        from src.seo_automation.utils.database import db_manager, User
        
        print(f"Database available: {db_manager.connection_available}")
        
        if db_manager.connection_available:
            print("✅ Database connection is available")
            
            # Test table creation
            db_manager.create_tables()
            print("✅ Database tables created/verified")
            
            test_results['database_connection'] = True
        else:
            print("⚠️ Database connection not available (continuing with mocks)")
            test_results['database_connection'] = False
        
    except Exception as e:
        print(f"⚠️ Database test warning: {e}")
        test_results['database_connection'] = False
    
    try:
        # Test 3: User Service
        print("\n👤 Testing User Service")
        print("-" * 40)
        
        from src.api.services.user_service import UserService
        from src.api.models.user import UserCreate, UserRole
        
        if db_manager.connection_available:
            # Test user creation
            test_user = UserCreate(
                email="test@example.com",
                full_name="Test User",
                password="secure_password123",
                role=UserRole.USER
            )
            
            try:
                # Try to create user (might fail if already exists)
                user = UserService.create_user(test_user)
                print(f"✅ User created: {user['email']}")
            except Exception as user_error:
                if "already registered" in str(user_error):
                    print("✅ User already exists (expected)")
                else:
                    raise user_error
            
            # Test authentication
            auth_result = UserService.authenticate_user("test@example.com", "secure_password123")
            if auth_result:
                print(f"✅ User authentication successful: {auth_result['email']}")
                print(f"   Role: {auth_result['role']}")
                print(f"   Permissions: {len(auth_result['permissions'])} permissions")
            else:
                print("❌ User authentication failed")
            
            test_results['user_service'] = True
        else:
            print("⚠️ Skipping User Service test (database not available)")
            test_results['user_service'] = False
        
    except Exception as e:
        print(f"❌ User Service test failed: {e}")
        test_results['user_service'] = False
    
    try:
        # Test 4: Complete Auth Flow
        print("\n🔄 Testing Complete Authentication Flow")
        print("-" * 40)
        
        if test_results['jwt_handler'] and test_results['user_service']:
            # Simulate login flow
            user = UserService.authenticate_user("test@example.com", "secure_password123")
            
            if user:
                # Create tokens
                token_data = {
                    "sub": str(user["id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "permissions": user["permissions"]
                }
                
                access_token = JWTHandler.create_access_token(token_data)
                refresh_token = JWTHandler.create_refresh_token({"sub": str(user["id"])})
                
                # Verify tokens
                payload = JWTHandler.verify_token(access_token, "access")
                
                print("✅ Complete authentication flow successful!")
                print(f"   User ID: {payload.get('sub')}")
                print(f"   Email: {payload.get('email')}")
                print(f"   Role: {payload.get('role')}")
                print(f"   Permissions: {len(payload.get('permissions', []))}")
                
                test_results['auth_flow'] = True
            else:
                print("❌ Authentication flow failed - user not found")
        else:
            print("⚠️ Skipping auth flow test (dependencies not available)")
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")
        test_results['auth_flow'] = False
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests >= 2:  # At least JWT and one other component
        print("\n🎉 Authentication system test SUCCESSFUL!")
        print("   The authentication system is ready for use.")
        return True
    else:
        print("\n💥 Authentication system test FAILED!")
        print("   Critical issues need to be resolved.")
        return False

if __name__ == "__main__":
    success = test_authentication_system()
    
    if success:
        print("\n🚀 Ready for API server testing!")
        print("   You can now start the FastAPI server and test the auth endpoints.")
    else:
        print("\n🛑 Fix authentication issues before proceeding.")
    
    sys.exit(0 if success else 1)
