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
print("查找刚才爬取的有封面数据")
print("=" * 60)

# 查找名称包含刚才爬取的影片的封面
test_names = ['声鸣远扬', '缥缈剑仙传', '万界独尊', '炼气十万年', '武碎星河']

for name in test_names:
    cursor.execute("""
        SELECT vod_id, vod_name, vod_pic 
        FROM sakura_movdetail 
        WHERE vod_name = %s
    """, (name,))
    
    result = cursor.fetchone()
    if result:
        vod_id, vod_name, vod_pic = result
        print(f"\n影片: {vod_name} (ID: {vod_id})")
        if vod_pic:
            print(f"封面: {vod_pic[:100]}...")
        else:
            print("封面: (空)")

conn.close()

print("\n" + "=" * 60)
