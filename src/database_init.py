#!/usr/bin/env python3
"""
Database Initialization Script
==============================

Creates database tables and ensures proper setup.
Run this script to initialize the database for the first time.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from seo_automation.utils.database import db_manager
from seo_automation.config.settings import settings

def main():
    """Initialize database tables."""
    print("🗃️  SEO Automation Database Initialization")
    print("=" * 50)
    
    print(f"Database URL: {settings.database_url}")
    print(f"Connection Available: {db_manager.connection_available}")
    
    if not db_manager.connection_available:
        print("❌ Database connection not available!")
        print("Please check your DATABASE_URL in .env file")
        return False
    
    try:
        print("\n📋 Creating database tables...")
        db_manager.create_tables()
        print("✅ Database tables created successfully!")
        
        # Test the connection
        session = db_manager.get_session()
        if session:
            print("✅ Database session test successful!")
            session.close()
        else:
            print("❌ Failed to create database session")
            return False
            
        print("\n🎉 Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
