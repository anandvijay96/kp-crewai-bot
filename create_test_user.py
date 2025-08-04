#!/usr/bin/env python3
"""
Create a test user for authentication testing
"""

import sys
import os
import sqlite3

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.auth.jwt_handler import JWTHandler

def create_test_user():
    """Create a fresh test user with proper password hash"""
    
    # Test credentials
    email = "demo@test.com"
    password = "demo123"
    full_name = "Demo User"
    
    print(f"🔐 Creating test user: {email}")
    print(f"🔑 Password: {password}")
    
    # Hash the password
    hashed_password = JWTHandler.hash_password(password)
    print(f"🛡️ Hashed password: {hashed_password}")
    
    # Test password verification
    is_valid = JWTHandler.verify_password(password, hashed_password)
    print(f"✅ Password verification test: {is_valid}")
    
    if not is_valid:
        print("❌ Password hashing/verification failed!")
        return False
    
    # Connect to database
    conn = sqlite3.connect('seo_automation.db')
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️ User {email} already exists, updating password...")
            cursor.execute('''
                UPDATE users 
                SET hashed_password = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (hashed_password, email))
        else:
            print(f"➕ Creating new user {email}...")
            cursor.execute('''
                INSERT INTO users (email, full_name, hashed_password, role, permissions, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                email,
                full_name,
                hashed_password,
                'user',
                '["view_campaign", "create_campaign", "edit_campaign", "view_blogs", "research_blogs", "generate_comments", "view_analytics", "run_agents"]',
                1
            ))
        
        conn.commit()
        print(f"✅ User {email} created/updated successfully!")
        
        # Verify the user was created
        cursor.execute('SELECT id, email, full_name, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            print(f"👤 User verification: ID={user[0]}, Email={user[1]}, Name={user[2]}, Role={user[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def test_authentication():
    """Test the authentication with the new user"""
    print("\n🔄 Testing authentication...")
    
    # Import user service
    from src.api.services.user_service import UserService
    
    email = "demo@test.com"
    password = "demo123"
    
    try:
        user = UserService.authenticate_user(email, password)
        
        if user:
            print("✅ Authentication successful!")
            print(f"👤 User: {user['email']}")
            print(f"🏷️ Role: {user['role']}")
            print(f"🔑 Permissions: {len(user['permissions'])} permissions")
            return True
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Test User for Authentication...")
    print("=" * 50)
    
    success = create_test_user()
    
    if success:
        test_success = test_authentication()
        
        if test_success:
            print("\n✨ Test user setup complete!")
            print("📝 Login credentials:")
            print("   Email: demo@test.com")
            print("   Password: demo123")
        else:
            print("\n❌ Authentication test failed!")
    else:
        print("\n❌ User creation failed!")
    
    print("=" * 50)
