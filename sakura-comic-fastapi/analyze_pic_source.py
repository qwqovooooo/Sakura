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
print("分析封面来源")
print("=" * 60)

# 统计不同来源的封面
cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic LIKE 'https://img%.doubanio.com%'")
douban_pics = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic LIKE 'http://www.yhdmp.net%'")
yhdmp_pics = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic LIKE 'https://pic%'")
other_pics = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic IS NOT NULL AND vod_pic != '' AND vod_pic NOT LIKE 'https://img%.doubanio.com%' AND vod_pic NOT LIKE 'http://www.yhdmp.net%' AND vod_pic NOT LIKE 'https://pic%'")
unknown_pics = cursor.fetchone()[0]

print(f"\n封面来源统计:")
print(f"  豆瓣图片: {douban_pics}")
print(f"  樱花动漫: {yhdmp_pics}")
print(f"  其他图床: {other_pics}")
print(f"  未知来源: {unknown_pics}")

# 查看一些非豆瓣的封面示例
cursor.execute("""
    SELECT vod_id, vod_name, vod_pic 
    FROM sakura_movdetail 
    WHERE vod_pic IS NOT NULL 
    AND vod_pic != '' 
    AND vod_pic NOT LIKE 'https://img%.doubanio.com%'
    LIMIT 5
""")
results = cursor.fetchall()

if results:
    print("\n非豆瓣封面示例:")
    for vod_id, vod_name, vod_pic in results:
        print(f"\n  影片: {vod_name}")
        print(f"  封面: {vod_pic}")

conn.close()

print("\n" + "=" * 60)
