import pymysql
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/movie')
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

print("=" * 60)
print("获取首页显示的电影封面")
print("=" * 60)

def get_douban_movie_info(douban_id):
    """根据豆瓣ID获取电影信息"""
    try:
        url = f"https://movie.douban.com/subject/{douban_id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            if 'img src="https://img' in html:
                start = html.find('img src="https://img')
                if start != -1:
                    start = html.find('https://img', start)
                    end = html.find('"', start)
                    if end != -1:
                        return html[start:end]
        return None
    except Exception as e:
        print(f"  获取失败: {e}")
        return None

# 首页显示的电影名称
movies_to_fetch = [
    "队友太弱所以贯彻辅助的宫廷魔法师，惨遭流放目标却是最强",
    "间谍过家家第3季",
    "叹气的亡灵想隐退第2季",
    "终末摩托游",
    "斗破苍穹年番",
    "野生的最终BOSS出现了",
    "我的英雄学院最终季",
    "婚戒物语第2季"
]

conn = pymysql.connect(
    host=host_db[0],
    user=user_pass[0],
    password=user_pass[1] if len(user_pass) > 1 else '',
    database=host_db[1] if len(host_db) > 1 else 'movie'
)
cursor = conn.cursor()

success_count = 0
fail_count = 0

for movie_name in movies_to_fetch:
    print(f"\n正在处理: {movie_name}")
    
    # 查找电影
    cursor.execute(
        "SELECT vod_id, vod_name, vod_douban_id, vod_pic FROM sakura_movdetail WHERE vod_name LIKE %s LIMIT 1",
        (f"%{movie_name}%",)
    )
    result = cursor.fetchone()
    
    if not result:
        print(f"  × 数据库中未找到")
        fail_count += 1
        continue
    
    vod_id, vod_name, douban_id, current_pic = result
    
    if current_pic:
        print(f"  ✓ 已有封面，跳过")
        continue
    
    if not douban_id or douban_id == 0:
        print(f"  × 没有豆瓣ID")
        fail_count += 1
        continue
    
    print(f"  豆瓣ID: {douban_id}")
    pic_url = get_douban_movie_info(douban_id)
    
    if pic_url:
        cursor.execute(
            "UPDATE sakura_movdetail SET vod_pic = %s WHERE vod_id = %s",
            (pic_url, vod_id)
        )
        conn.commit()
        success_count += 1
        print(f"  ✓ 成功: {pic_url[:60]}...")
    else:
        fail_count += 1
        print(f"  × 未找到封面")
    
    time.sleep(3)

cursor.close()
conn.close()

print("\n" + "=" * 60)
print(f"完成！成功: {success_count} 条，失败: {fail_count} 条")
print("=" * 60)
