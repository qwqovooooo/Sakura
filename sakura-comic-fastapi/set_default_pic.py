"""
为所有没有封面的影片设置默认占位图
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/movie')
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

print("=" * 60)
print("设置默认占位封面")
print("=" * 60)

conn = pymysql.connect(
    host=host_db[0],
    user=user_pass[0],
    password=user_pass[1] if len(user_pass) > 1 else '',
    database=host_db[1] if len(host_db) > 1 else 'movie'
)

cursor = conn.cursor()

# 使用一个美观的默认封面图（在线图片，确保能访问）
default_pic = "https://via.placeholder.com/200x280/667eea/ffffff?text=%E6%9A%82%E6%97%A0%E5%B0%81%E9%9D%A2"

# 统计当前空封面数量
cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic IS NULL OR vod_pic = ''")
empty_count = cursor.fetchone()[0]

print(f"\n找到 {empty_count} 条没有封面的记录")

if empty_count > 0:
    print(f"正在设置默认封面...")
    cursor.execute(
        "UPDATE sakura_movdetail SET vod_pic = %s WHERE vod_pic IS NULL OR vod_pic = ''",
        (default_pic,)
    )
    conn.commit()
    print(f"✓ 已成功更新 {cursor.rowcount} 条记录")
else:
    print("所有记录都已有封面")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("完成！刷新页面即可看到默认封面")
print("=" * 60)
