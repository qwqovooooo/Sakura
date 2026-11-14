import requests

# 测试专门的短剧资源站
short_drama_apis = [
    ("非凡资源", "https://cj.ffzyapi.com/api.php/provide/vod/"),
    ("量子资源", "https://cj.lziapi.com/api.php/provide/vod/"),
    ("新浪资源", "https://api.xinlangapi.com/xinlang.php/provide/vod/"),
]

headers = {'User-Agent': 'Mozilla/5.0'}
test_name = '临时情侣'

print("=" * 60)
print(f"搜索短剧: {test_name}")
print("=" * 60)

for name, url in short_drama_apis:
    print(f"\n测试: {name}")
    params = {
        'ac': 'detail',
        'wd': test_name
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if 'list' in data and len(data['list']) > 0:
            movie = data['list'][0]
            pic = movie.get('vod_pic', '')
            print(f"  ✓ 找到了！")
            print(f"    ID: {movie.get('vod_id')}")
            print(f"    名称: {movie.get('vod_name')}")
            print(f"    封面: {'有' if pic else '无'}")
            if pic:
                print(f"    链接: {pic[:60]}...")
        else:
            print(f"  × 未找到")
            
    except requests.exceptions.Timeout:
        print(f"  × 连接超时")
    except requests.exceptions.ConnectionError:
        print(f"  × 连接失败")
    except Exception as e:
        print(f"  × 错误: {str(e)[:40]}")

print("\n" + "=" * 60)
