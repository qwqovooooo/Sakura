"""
测试不同的影视资源API，查看哪个有封面数据
"""
import requests
import json

# 测试多个资源站API
api_list = [
    ("红牛资源", "https://www.hongniuzyw.com/api.php/provide/vod/"),
    ("八戒资源", "https://api.apibdzy.com/api.php/provide/vod/"),
    ("北斗资源", "https://bdzym3u8.com/api.php/provide/vod/"),
    ("快播资源", "https://www.kuaibozy.com/api.php/provide/vod/"),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

params = {
    'ac': 'detail',
    'pg': 1
}

print("=" * 60)
print("测试资源站API封面数据")
print("=" * 60)

for name, url in api_list:
    print(f"\n正在测试: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'list' in data and len(data['list']) > 0:
                movie = data['list'][0]
                vod_pic = movie.get('vod_pic', '')
                
                print(f"  ✓ 连接成功")
                print(f"  影片数量: {len(data['list'])}")
                print(f"  示例影片: {movie.get('vod_name', '未知')}")
                print(f"  封面字段: {'有' if vod_pic else '无'}")
                if vod_pic:
                    print(f"  封面链接: {vod_pic[:80]}...")
            else:
                print(f"  ✓ 连接成功，但无数据")
        else:
            print(f"  × 请求失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"  × 连接超时")
    except requests.exceptions.ConnectionError:
        print(f"  × 连接失败（网络问题）")
    except Exception as e:
        print(f"  × 错误: {str(e)[:50]}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
