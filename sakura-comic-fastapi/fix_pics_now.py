import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/movie')
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

print("=" * 60)
print("强制更新图片链接为默认占位图")
print("=" * 60)

try:
    conn = pymysql.connect(
        host=host_db[0],
        user=user_pass[0],
        password=user_pass[1] if len(user_pass) > 1 else '',
        database=host_db[1] if len(host_db) > 1 else 'movie',
        autocommit=False  # 关闭自动提交，手动控制
    )
    
    cursor = conn.cursor()
    
    default_pic = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='280'%3E%3Crect fill='%23f0f0f0' width='200' height='280'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%23999' font-size='16'%3E暂无封面%3C/text%3E%3C/svg%3E"
    
    print("\n正在更新 sakura_movdetail 表...")
    cursor.execute("UPDATE sakura_movdetail SET vod_pic = %s WHERE vod_pic != %s", (default_pic, default_pic))
    count = cursor.rowcount
    print(f"✓ 准备更新 {count} 条记录")
    
    # 手动提交
    conn.commit()
    print("✓ 已提交到数据库")
    
    # 验证更新
    cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE vod_pic LIKE 'data:image%'")
    verify_count = cursor.fetchone()[0]
    print(f"✓ 验证：现在有 {verify_count} 条记录使用默认占位图")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ 更新完成！")
    print("=" * 60)
    print("\n现在刷新浏览器页面，应该能看到'暂无封面'了")
    
except Exception as e:
    print(f"\n× 错误: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
