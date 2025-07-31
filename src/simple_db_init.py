#!/usr/bin/env python3
"""
Simple Database Initialization Script
====================================

Creates SQLite database tables without complex dependencies.
"""

import sqlite3
import os

def create_tables():
    """Create database tables directly with SQLite."""
    db_path = "./seo_automation.db"
    
    print(f"🗃️  Creating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create blogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                domain_authority INTEGER,
                category TEXT,
                status TEXT DEFAULT 'active',
                analysis_metadata TEXT,  -- JSON as TEXT
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create blog_posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content_summary TEXT,
                author TEXT,
                publication_date TEXT,
                word_count INTEGER DEFAULT 0,
                has_comments BOOLEAN DEFAULT 0,
                tags TEXT,  -- JSON as TEXT
                comment_worthiness_score INTEGER DEFAULT 0,
                engagement_potential TEXT DEFAULT 'low',
                analysis_data TEXT,  -- JSON as TEXT
                analyzed_at TIMESTAMP,
                status TEXT DEFAULT 'discovered',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                quality_score REAL,
                status TEXT DEFAULT 'pending',
                generated_by TEXT,
                cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                permissions TEXT,  -- JSON as TEXT
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create cost_tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create agent_executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                task_description TEXT NOT NULL,
                context_data TEXT,  -- JSON as TEXT
                model_name TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                status TEXT NOT NULL,
                result_data TEXT,  -- JSON as TEXT
                cost REAL,
                tokens_used INTEGER,
                execution_time REAL
            )
        ''')
        
        conn.commit()
        print("✅ Database tables created successfully!")
        
        # Test by inserting a sample blog
        cursor.execute('''
            INSERT OR IGNORE INTO blogs (url, domain, category, analysis_metadata)
            VALUES (?, ?, ?, ?)
        ''', ('https://example.com', 'example.com', 'test', '{"test": true}'))
        
        conn.commit()
        
        # Check if data was inserted
        cursor.execute('SELECT COUNT(*) FROM blogs')
        count = cursor.fetchone()[0]
        print(f"✅ Database test successful! Found {count} blog(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n🎉 Database initialization complete!")
    else:
        print("\n❌ Database initialization failed!")
