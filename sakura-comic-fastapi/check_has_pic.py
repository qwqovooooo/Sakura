import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/movie')
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

conn = pymysql.connect(
    host=host_db[0],
    user=user_pass[0],
    password=user_pass[1] if len(user_pass) > 1 else '',
    database=host_db[1] if len(host_db) > 1 else 'movie'
)

cursor = conn.cursor()

print("=" * 60)
print("检查有封面的记录示例")
print("=" * 60)

# 查找有封面的记录
cursor.execute("SELECT vod_id, vod_name, vod_pic FROM sakura_movdetail WHERE vod_pic IS NOT NULL AND vod_pic != '' LIMIT 5")
results = cursor.fetchall()

print("\n有封面的记录示例:")
for i, (vod_id, vod_name, vod_pic) in enumerate(results, 1):
    print(f"\n{i}. ID: {vod_id}")
    print(f"   名称: {vod_name}")
    print(f"   封面: {vod_pic[:100]}...")
    
conn.close()
