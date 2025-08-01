import sqlite3

conn = sqlite3.connect('seo_automation.db')
cursor = conn.cursor()

tables = ['users', 'blogs', 'blog_posts', 'comments', 'cost_tracking', 'agent_executions']

print("Database table row counts:")
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{table}: {count} rows')

# Check blog_posts structure
cursor.execute("PRAGMA table_info(blog_posts)")
columns = cursor.fetchall()
print("\nblog_posts table structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
