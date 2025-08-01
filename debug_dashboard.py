import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('seo_automation.db')
cursor = conn.cursor()

print("=== Dashboard Query Debug ===")

# 1. Test blog_posts count
cursor.execute("SELECT COUNT(*) FROM blog_posts")
blog_count = cursor.fetchone()[0]
print(f"📊 Total blog_posts: {blog_count}")

# 2. Test recent agent_executions
cursor.execute("""
    SELECT COUNT(DISTINCT id) FROM agent_executions 
    WHERE created_at >= datetime('now', '-30 days')
    AND status = 'running' OR status = 'completed'
""")
campaigns = cursor.fetchone()[0]
print(f"🏃 Active campaigns: {campaigns}")

# 3. Test comments
cursor.execute("SELECT COUNT(*) FROM comments WHERE status IN ('generated', 'posted')")
comments = cursor.fetchone()[0]
print(f"💬 Comments generated: {comments}")

# 4. Test recent campaigns query
cursor.execute("""
    SELECT agent_type, parameters, created_at, status,
           COUNT(*) as execution_count
    FROM agent_executions 
    WHERE created_at >= datetime('now', '-30 days')
    GROUP BY agent_type, DATE(created_at)
    ORDER BY created_at DESC
    LIMIT 5
""")
recent = cursor.fetchall()
print(f"📅 Recent campaigns found: {len(recent)}")

# 5. Test top blogs query  
cursor.execute("""
    SELECT title, url, domain_authority, 
           (SELECT COUNT(*) FROM comments WHERE blog_post_id = blog_posts.id) as comment_count
    FROM blog_posts 
    WHERE domain_authority IS NOT NULL AND domain_authority > 0
    ORDER BY domain_authority DESC, comment_count DESC
    LIMIT 5
""")
top_blogs = cursor.fetchall()
print(f"🏆 Top blogs found: {len(top_blogs)}")

# 6. Show actual blog_posts data
cursor.execute("SELECT id, title, url, analysis_data FROM blog_posts LIMIT 5")
posts = cursor.fetchall()
print(f"\n📝 Blog posts in database:")
for post in posts:
    print(f"  - ID: {post[0]}, Title: {post[1][:50]}...")
    if post[3]:
        import json
        try:
            analysis = json.loads(post[3])
            print(f"    DA: {analysis.get('domainAuthority', 'N/A')}, PA: {analysis.get('pageAuthority', 'N/A')}")
        except:
            print(f"    Analysis: {post[3][:100]}...")

conn.close()
