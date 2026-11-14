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
print("检查新爬取数据的封面")
print("=" * 60)

# 查看最新的10条数据（按ID降序）
cursor.execute("""
    SELECT vod_id, vod_name, LEFT(vod_pic, 80) as pic 
    FROM sakura_movdetail 
    ORDER BY vod_id DESC 
    LIMIT 10
""")
results = cursor.fetchall()

print("\n最新的10条数据:")
for i, (vod_id, vod_name, vod_pic) in enumerate(results, 1):
    pic_status = "有封面" if vod_pic else "无封面"
    print(f"{i}. {vod_name} (ID: {vod_id}) - {pic_status}")
    if vod_pic:
        print(f"   {vod_pic}...")

conn.close()

print("\n" + "=" * 60)
