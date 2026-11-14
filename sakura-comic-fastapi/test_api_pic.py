import requests
import json

# 测试API返回的数据
api_url = "https://www.hongniuzyw.com/api.php/provide/vod/"
params = {
    'ac': 'detail',
    'pg': 1
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(api_url, params=params, headers=headers, timeout=30)
data = response.json()

print("=" * 60)
print("检查API返回的封面数据")
print("=" * 60)

if 'list' in data and len(data['list']) > 0:
    # 查看前3条数据
    for i, movie in enumerate(data['list'][:3], 1):
        print(f"\n第{i}条:")
        print(f"  ID: {movie.get('vod_id')}")
        print(f"  名称: {movie.get('vod_name')}")
        print(f"  封面: {movie.get('vod_pic', '无')}")
        print(f"  封面长度: {len(movie.get('vod_pic', ''))}")
else:
    print("未获取到数据")
