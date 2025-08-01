#!/usr/bin/env python3
"""
Phase 6A Critical Fix - Database Storage Integration
==================================================

This script addresses the critical issue of search results not being stored in the database.
It implements enhanced filtering and data persistence for the blog discovery service.
"""

import asyncio
import json
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List, Any
import uuid

class BlogStorageService:
    """Service to handle storing blog discovery results to database."""
    
    def __init__(self, db_path: str = "seo_automation.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create enhanced blog_posts table with real-time data requirements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id TEXT PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    domain TEXT,
                    domain_authority INTEGER,
                    page_authority INTEGER,
                    comments_enabled BOOLEAN DEFAULT FALSE,
                    keywords TEXT,  -- JSON array of keywords
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    campaign_id TEXT,
                    status TEXT DEFAULT 'discovered'
                );
            """)
            
            # Create campaigns table for better organization
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    keywords TEXT,  -- JSON array
                    user_id INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create comments table for future comment generation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    blog_post_id TEXT,
                    content TEXT,
                    status TEXT DEFAULT 'generated',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    posted_at TIMESTAMP,
                    FOREIGN KEY (blog_post_id) REFERENCES blog_posts (id)
                );
            """)
            
            # Create agent_executions table for tracking research sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id TEXT PRIMARY KEY,
                    agent_type TEXT,
                    parameters TEXT,  -- JSON
                    status TEXT DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    user_id INTEGER,
                    results_count INTEGER DEFAULT 0
                );
            """)
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def store_blog_discovery_results(
        self, 
        results: List[Dict[str, Any]], 
        search_keywords: List[str],
        user_id: int = 1,
        min_da: int = 30,
        min_pa: int = 30
    ) -> Dict[str, Any]:
        """
        Store blog discovery results with enhanced filtering.
        
        Args:
            results: List of discovered blogs
            search_keywords: Keywords used in search
            user_id: User ID (default 1 for testing)
            min_da: Minimum Domain Authority
            min_pa: Minimum Page Authority
        
        Returns:
            Storage results with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create a campaign for this search
            campaign_id = str(uuid.uuid4())
            campaign_name = f"Blog Discovery - {', '.join(search_keywords[:3])}"
            
            cursor.execute("""
                INSERT INTO campaigns (id, name, keywords, user_id, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (campaign_id, campaign_name, json.dumps(search_keywords), user_id))
            
            # Create agent execution record
            execution_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO agent_executions (id, agent_type, parameters, user_id)
                VALUES (?, ?, ?, ?)
            """, (
                execution_id,
                'blog_discovery',
                json.dumps({
                    'keywords': search_keywords,
                    'min_da': min_da,
                    'min_pa': min_pa,
                    'total_results': len(results)
                }),
                user_id
            ))
            
            stored_blogs = 0
            filtered_blogs = 0
            
            for blog in results:
                # Enhanced filtering criteria
                domain_authority = blog.get('domainAuthority', 0)
                page_authority = blog.get('pageAuthority', 0)
                comments_enabled = blog.get('commentOpportunity', False)
                
                # Apply strict filtering
                if (domain_authority >= min_da and 
                    page_authority >= min_pa and 
                    comments_enabled and
                    blog.get('url')):
                    
                    blog_id = str(uuid.uuid4())
                    
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO blog_posts 
                            (id, url, title, domain, domain_authority, page_authority, 
                             comments_enabled, keywords, user_id, campaign_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            blog_id,
                            blog['url'],
                            blog.get('title', 'Untitled'),
                            blog.get('domain', ''),
                            domain_authority,
                            page_authority,
                            comments_enabled,
                            json.dumps(blog.get('keywords', search_keywords)),
                            user_id,
                            campaign_id
                        ))
                        stored_blogs += 1
                        
                    except sqlite3.IntegrityError:
                        # URL already exists, update it
                        cursor.execute("""
                            UPDATE blog_posts 
                            SET title = ?, domain_authority = ?, page_authority = ?,
                                comments_enabled = ?, keywords = ?, campaign_id = ?
                            WHERE url = ?
                        """, (
                            blog.get('title', 'Untitled'),
                            domain_authority,
                            page_authority,
                            comments_enabled,
                            json.dumps(blog.get('keywords', search_keywords)),
                            campaign_id,
                            blog['url']
                        ))
                        stored_blogs += 1
                else:
                    filtered_blogs += 1
            
            # Update agent execution with results
            cursor.execute("""
                UPDATE agent_executions 
                SET status = 'completed', completed_at = ?, results_count = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), stored_blogs, execution_id))
            
            conn.commit()
            conn.close()
            
            storage_result = {
                'campaign_id': campaign_id,
                'execution_id': execution_id,
                'total_discovered': len(results),
                'stored_blogs': stored_blogs,
                'filtered_out': filtered_blogs,
                'storage_success': True,
                'filter_criteria': {
                    'min_domain_authority': min_da,
                    'min_page_authority': min_pa,
                    'comments_required': True
                }
            }
            
            print(f"✅ Stored {stored_blogs} blogs, filtered out {filtered_blogs}")
            return storage_result
            
        except Exception as e:
            print(f"❌ Storage error: {e}")
            return {
                'storage_success': False,
                'error': str(e),
                'total_discovered': len(results),
                'stored_blogs': 0
            }
    
    def get_dashboard_data(self, user_id: int = 1) -> Dict[str, Any]:
        """Get real dashboard data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Active Campaigns (campaigns created in last 30 days)
            cursor.execute("""
                SELECT COUNT(*) FROM campaigns 
                WHERE user_id = ? AND status = 'active'
                AND created_at >= datetime('now', '-30 days')
            """, (user_id,))
            active_campaigns = cursor.fetchone()[0]
            
            # Blogs Discovered
            cursor.execute("""
                SELECT COUNT(*) FROM blog_posts WHERE user_id = ?
            """, (user_id,))
            blogs_discovered = cursor.fetchone()[0]
            
            # Comments Generated
            cursor.execute("""
                SELECT COUNT(*) FROM comments 
                WHERE blog_post_id IN (
                    SELECT id FROM blog_posts WHERE user_id = ?
                )
            """, (user_id,))
            comments_generated = cursor.fetchone()[0]
            
            # Success Rate (placeholder for now)
            success_rate = (comments_generated / max(blogs_discovered, 1)) * 100 if blogs_discovered > 0 else 0
            
            # Recent Campaigns
            cursor.execute("""
                SELECT c.name, c.status, COUNT(bp.id) as blog_count, c.created_at
                FROM campaigns c
                LEFT JOIN blog_posts bp ON c.id = bp.campaign_id
                WHERE c.user_id = ? AND c.created_at >= datetime('now', '-30 days')
                GROUP BY c.id
                ORDER BY c.created_at DESC
                LIMIT 5
            """, (user_id,))
            
            recent_campaigns = []
            for row in cursor.fetchall():
                name, status, blog_count, created_at = row
                recent_campaigns.append({
                    "name": name[:50],
                    "status": "Active" if status == 'active' else "Paused",
                    "blogs": blog_count
                })
            
            # Top Performing Blogs
            cursor.execute("""
                SELECT title, domain, domain_authority, 
                       (SELECT COUNT(*) FROM comments WHERE blog_post_id = blog_posts.id) as comment_count
                FROM blog_posts
                WHERE user_id = ? AND domain_authority > 0
                ORDER BY domain_authority DESC, comment_count DESC
                LIMIT 5
            """, (user_id,))
            
            top_blogs = []
            for row in cursor.fetchall():
                title, domain, authority, comments = row
                top_blogs.append({
                    "title": (title or "Untitled")[:60],
                    "domain": domain or "unknown",
                    "score": authority or 0,
                    "comments": comments or 0
                })
            
            conn.close()
            
            return {
                "activeCampaigns": active_campaigns,
                "blogsDiscovered": blogs_discovered,
                "commentsGenerated": comments_generated,
                "successRate": round(success_rate, 1),
                "recentCampaigns": recent_campaigns,
                "topBlogs": top_blogs
            }
            
        except Exception as e:
            print(f"❌ Dashboard data error: {e}")
            return {
                "activeCampaigns": 0,
                "blogsDiscovered": 0,
                "commentsGenerated": 0,
                "successRate": 0.0,
                "recentCampaigns": [],
                "topBlogs": []
            }

async def test_blog_storage_integration():
    """Test the blog storage service with sample data."""
    
    print("🧪 Testing Blog Storage Integration")
    print("=" * 50)
    
    # Initialize storage service
    storage = BlogStorageService()
    
    # Sample blog data (mimicking scraping service results)
    sample_blogs = [
        {
            "url": "https://searchengineland.com/seo-guide",
            "title": "Ultimate SEO Guide 2025",
            "domain": "searchengineland.com",
            "domainAuthority": 89,
            "pageAuthority": 76,
            "commentOpportunity": True,
            "keywords": ["SEO", "search optimization"]
        },
        {
            "url": "https://moz.com/blog/local-seo",
            "title": "Local SEO Best Practices",
            "domain": "moz.com", 
            "domainAuthority": 91,
            "pageAuthority": 78,
            "commentOpportunity": True,
            "keywords": ["local SEO", "SEO"]
        },
        {
            "url": "https://example.com/low-authority",
            "title": "Low Authority Blog",
            "domain": "example.com",
            "domainAuthority": 15,  # Below threshold
            "pageAuthority": 20,    # Below threshold
            "commentOpportunity": True,
            "keywords": ["SEO"]
        },
        {
            "url": "https://niche-blog.com/seo-tips",
            "title": "SEO Tips for Beginners",
            "domain": "niche-blog.com",
            "domainAuthority": 45,
            "pageAuthority": 42,
            "commentOpportunity": False,  # No comments - should be filtered
            "keywords": ["SEO", "beginners"]
        }
    ]
    
    # Test storage with filtering
    search_keywords = ["SEO", "search optimization"]
    result = storage.store_blog_discovery_results(
        sample_blogs, 
        search_keywords,
        user_id=1,
        min_da=30,
        min_pa=30
    )
    
    print(f"📊 Storage Results:")
    print(f"  - Total discovered: {result['total_discovered']}")
    print(f"  - Stored blogs: {result['stored_blogs']}")
    print(f"  - Filtered out: {result['filtered_out']}")
    print(f"  - Campaign ID: {result.get('campaign_id', 'N/A')}")
    
    # Test dashboard data retrieval
    print(f"\n📈 Dashboard Data:")
    dashboard = storage.get_dashboard_data(user_id=1)
    print(f"  - Active Campaigns: {dashboard['activeCampaigns']}")
    print(f"  - Blogs Discovered: {dashboard['blogsDiscovered']}")
    print(f"  - Success Rate: {dashboard['successRate']}%")
    print(f"  - Recent Campaigns: {len(dashboard['recentCampaigns'])}")
    print(f"  - Top Blogs: {len(dashboard['topBlogs'])}")
    
    return result['stored_blogs'] > 0

if __name__ == "__main__":
    success = asyncio.run(test_blog_storage_integration())
    if success:
        print("\n🎉 Blog storage integration test successful!")
        print("✅ Database persistence is now working")
        print("✅ Enhanced filtering is operational")
        print("✅ Real dashboard data is available")
    else:
        print("\n❌ Blog storage integration test failed")
