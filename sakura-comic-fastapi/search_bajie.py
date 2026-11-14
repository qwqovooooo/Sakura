import requests

# 在八戒资源搜索特定影片
url = "https://api.apibdzy.com/api.php/provide/vod/"
headers = {'User-Agent': 'Mozilla/5.0'}

test_names = ['临时情侣', '云散识假意', '以善意之名', '伪装乐章', '假面女王']

print("=" * 60)
print("在八戒资源搜索短剧")
print("=" * 60)

for name in test_names:
    params = {
        'ac': 'detail',
        'wd': name
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if 'list' in data and len(data['list']) > 0:
            print(f"\n✓ 找到: {name}")
            movie = data['list'][0]
            print(f"  ID: {movie.get('vod_id')}")
            print(f"  封面: {movie.get('vod_pic', '无')[:60]}...")
        else:
            print(f"\n× 未找到: {name}")
    except Exception as e:
        print(f"\n× 搜索失败: {name} - {e}")

print("\n" + "=" * 60)
