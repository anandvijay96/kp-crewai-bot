import sqlite3
import json
from datetime import datetime

# Connect to database
conn = sqlite3.connect('seo_automation.db')
cursor = conn.cursor()

# Test blog data
blog_data = {
    'url': 'https://example-blog.com/test-post',
    'title': 'Test Blog Post for Database',
    'snippet': 'This is a test snippet for database insertion',
    'domain': 'example-blog.com',
    'domainAuthority': 45,
    'pageAuthority': 38,
    'discoveredAt': datetime.now().isoformat()
}

try:
    # Insert test data
    cursor.execute("""
        INSERT INTO blog_posts (
            url, title, content_summary, has_comments, 
            analysis_data, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        blog_data['url'],
        blog_data['title'],
        blog_data['snippet'],
        1,  # has_comments = true
        json.dumps({
            'domainAuthority': blog_data['domainAuthority'],
            'pageAuthority': blog_data['pageAuthority'],
            'domain': blog_data['domain'],
            'discoveredAt': blog_data['discoveredAt']
        }),
        'discovered',
        blog_data['discoveredAt']
    ])
    
    conn.commit()
    print(f"✅ Successfully inserted test blog: {blog_data['title']} (ID: {cursor.lastrowid})")
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM blog_posts")
    count = cursor.fetchone()[0]
    print(f"📊 Total blog_posts in database: {count}")
    
    # Show the inserted record
    cursor.execute("SELECT id, title, url, status FROM blog_posts WHERE id = ?", (cursor.lastrowid,))
    record = cursor.fetchone()
    if record:
        print(f"📝 Inserted record: ID={record[0]}, Title='{record[1]}', URL='{record[2]}', Status='{record[3]}'")
    
except Exception as e:
    print(f"❌ Database insertion failed: {e}")
    conn.rollback()
finally:
    conn.close()
