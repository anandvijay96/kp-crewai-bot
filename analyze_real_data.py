#!/usr/bin/env python3
"""
Real Data Analysis Script
========================

Analyze the actual database to understand what real data we have for the dashboard.
"""

import sqlite3
import json
from datetime import datetime, timedelta

def analyze_database():
    """Analyze the database structure and content."""
    
    print("🔍 Analyzing SEO Automation Database")
    print("=" * 50)
    
    conn = sqlite3.connect('seo_automation.db')
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Analyze each table
        for table_name in [t[0] for t in tables]:
            print(f"\n📋 Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("🏗️  Schema:")
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_str = " (PRIMARY KEY)" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  - {col_name}: {col_type}{pk_str}{not_null_str}{default_str}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"📊 Row count: {count}")
            
            # Show sample data if rows exist
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_rows = cursor.fetchall()
                
                print("🔍 Sample data:")
                col_names = [col[1] for col in columns]
                
                for i, row in enumerate(sample_rows):
                    print(f"  Row {i+1}:")
                    for j, value in enumerate(row):
                        if j < len(col_names):
                            # Truncate long values
                            str_value = str(value)
                            if len(str_value) > 50:
                                str_value = str_value[:47] + "..."
                            print(f"    {col_names[j]}: {str_value}")
                    print()
        
        print("\n" + "=" * 50)
        print("📈 Dashboard Data Analysis")
        print("-" * 30)
        
        # Calculate real dashboard metrics
        
        # 1. Active Campaigns (from blog_posts or research tasks)
        cursor.execute("SELECT COUNT(DISTINCT url) FROM blog_posts WHERE status = 'active' OR status IS NULL;")
        active_campaigns = cursor.fetchone()[0]
        
        # 2. Blogs Discovered (total blogs in blog_posts)
        cursor.execute("SELECT COUNT(*) FROM blog_posts;")
        blogs_discovered = cursor.fetchone()[0]
        
        # 3. Comments Generated
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'generated' OR status = 'posted';")
        comments_generated = cursor.fetchone()[0]
        
        # 4. Success Rate (comments posted vs generated)
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'posted';")
        comments_posted = cursor.fetchone()[0]
        
        success_rate = (comments_posted / comments_generated * 100) if comments_generated > 0 else 0
        
        print(f"📊 Real Dashboard Metrics:")
        print(f"  - Active Campaigns: {active_campaigns}")
        print(f"  - Blogs Discovered: {blogs_discovered}")
        print(f"  - Comments Generated: {comments_generated}")
        print(f"  - Comments Posted: {comments_posted}")
        print(f"  - Success Rate: {success_rate:.1f}%")
        
        # 5. Recent Campaigns (recent blog discoveries)
        print(f"\n📅 Recent Campaigns:")
        cursor.execute("""
            SELECT url, title, COUNT(*) as blog_count, 
                   MAX(created_at) as last_activity
            FROM blog_posts 
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY url, title
            ORDER BY last_activity DESC
            LIMIT 5;
        """)
        
        recent_campaigns = cursor.fetchall()
        for campaign in recent_campaigns:
            url, title, count, last_activity = campaign
            title = title[:50] + "..." if title and len(title) > 50 else title
            print(f"  - {title or url}: {count} blogs (last: {last_activity})")
        
        # 6. Top Performing Blogs
        print(f"\n🏆 Top Performing Blogs:")
        cursor.execute("""
            SELECT bp.title, bp.url, bp.domain_authority, 
                   COUNT(c.id) as comment_count
            FROM blog_posts bp
            LEFT JOIN comments c ON bp.id = c.blog_post_id
            WHERE bp.domain_authority IS NOT NULL
            GROUP BY bp.id
            ORDER BY bp.domain_authority DESC, comment_count DESC
            LIMIT 5;
        """)
        
        top_blogs = cursor.fetchall()
        for blog in top_blogs:
            title, url, authority, comments = blog
            title = title[:50] + "..." if title and len(title) > 50 else title
            print(f"  - {title}: DA {authority}, {comments} comments")
        
        # Generate real data structure for API
        dashboard_data = {
            "activeCampaigns": active_campaigns,
            "blogsDiscovered": blogs_discovered, 
            "commentsGenerated": comments_generated,
            "successRate": round(success_rate, 1),
            "recentCampaigns": [],
            "topBlogs": []
        }
        
        # Format recent campaigns
        for campaign in recent_campaigns:
            url, title, count, last_activity = campaign
            status = "Active" if count > 0 else "Paused"
            dashboard_data["recentCampaigns"].append({
                "name": title[:50] if title else url[:50],
                "status": status,
                "blogs": count
            })
        
        # Format top blogs
        for blog in top_blogs:
            title, url, authority, comments = blog
            domain = url.split('/')[2] if '://' in url else url
            dashboard_data["topBlogs"].append({
                "title": title[:50] if title else "Untitled",
                "domain": domain,
                "score": authority or 0,
                "comments": comments
            })
        
        print(f"\n🎯 Generated Dashboard Data Structure:")
        print(json.dumps(dashboard_data, indent=2))
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return None
        
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_database()
