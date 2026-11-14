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
print("检查封面字段详情")
print("=" * 60)

# 检查前10条记录的完整封面信息
cursor.execute("SELECT vod_id, vod_name, vod_pic FROM sakura_movdetail LIMIT 10")
results = cursor.fetchall()

print("\n前10条记录的封面信息:")
for i, (vod_id, vod_name, vod_pic) in enumerate(results, 1):
    print(f"\n{i}. ID: {vod_id}")
    print(f"   名称: {vod_name}")
    print(f"   封面: {vod_pic if vod_pic else '(空)'}")
    print(f"   封面长度: {len(vod_pic) if vod_pic else 0}")

# 统计情况
cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic IS NULL OR vod_pic = ''")
empty_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sakura_movdetail")
total_count = cursor.fetchone()[0]

print("\n" + "=" * 60)
print(f"总记录数: {total_count}")
print(f"空封面数: {empty_count}")
print(f"有封面数: {total_count - empty_count}")
print("=" * 60)

conn.close()
