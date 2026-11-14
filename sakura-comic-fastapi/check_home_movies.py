import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root', database='movie')
cursor = conn.cursor()

# 查看首页会显示的电影（最新的20条）
cursor.execute("SELECT vod_id, vod_name, vod_pic FROM sakura_movdetail ORDER BY vod_id DESC LIMIT 20")
movies = cursor.fetchall()

print("首页显示的电影：\n")
for vod_id, vod_name, vod_pic in movies:
    has_pic = "有封面" if vod_pic else "无封面"
    print(f"{vod_id} - {vod_name[:30]} - {has_pic}")
    if vod_pic:
        print(f"  图片: {vod_pic[:80]}")

conn.close()
