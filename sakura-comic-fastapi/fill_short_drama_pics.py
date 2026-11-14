"""
从量子资源为没有封面的短剧补充封面
"""
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
print("从量子资源补充短剧封面")
print("=" * 60)

def get_pic_from_liangzi(vod_name):
    """从量子资源搜索获取封面"""
    try:
        url = "https://cj.lziapi.com/api.php/provide/vod/"
        params = {
            'ac': 'detail',
            'wd': vod_name
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if 'list' in data and len(data['list']) > 0:
            movie = data['list'][0]
            # 名称要匹配
            if movie.get('vod_name') == vod_name:
                return movie.get('vod_pic', '')
        
        return None
        
    except Exception as e:
        print(f"  搜索失败: {e}")
        return None

def main():
    try:
        conn = pymysql.connect(
            host=host_db[0],
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else '',
            database=host_db[1] if len(host_db) > 1 else 'movie',
            autocommit=False
        )
        
        cursor = conn.cursor()
        
        # 获取所有没有封面的影片（限制100条，避免太多）
        cursor.execute("""
            SELECT vod_id, vod_name 
            FROM sakura_movdetail 
            WHERE vod_pic IS NULL OR vod_pic = ''
            LIMIT 100
        """)
        
        movies = cursor.fetchall()
        
        print(f"\n找到 {len(movies)} 条没有封面的影片")
        print("\n开始从量子资源搜索封面...")
        
        success_count = 0
        fail_count = 0
        
        for i, (vod_id, vod_name) in enumerate(movies, 1):
            print(f"\n[{i}/{len(movies)}] {vod_name}")
            
            pic_url = get_pic_from_liangzi(vod_name)
            
            if pic_url:
                # 更新数据库
                cursor.execute(
                    "UPDATE sakura_movdetail SET vod_pic = %s WHERE vod_id = %s",
                    (pic_url, vod_id)
                )
                conn.commit()
                success_count += 1
                print(f"  ✓ 成功: {pic_url[:60]}...")
            else:
                fail_count += 1
                print(f"  × 未找到")
            
            # 避免请求太频繁
            time.sleep(1)
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"完成！成功: {success_count} 条，失败: {fail_count} 条")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    main()
