import requests
import json

# 测试API返回的数据（正确的路径是 /vod_list 而不是 /api/vod_list）
url = "http://localhost:8000/vod_list?movtype=1&page=1"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"返回数据类型: {type(data)}")
    print(f"返回数据键: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
    
    if isinstance(data, dict) and 'data' in data:
        movies = data['data']
        print(f"\n总共 {len(movies)} 条电影数据")
        print("\n前3条数据:")
        for i, movie in enumerate(movies[:3]):
            print(f"\n第 {i+1} 条:")
            print(f"  vod_id: {movie.get('vod_id')}")
            print(f"  vod_name: {movie.get('vod_name')}")
            print(f"  vod_pic: {movie.get('vod_pic')}")
            print(f"  vod_remarks: {movie.get('vod_remarks')}")
    else:
        print(f"\n完整返回数据:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        
except Exception as e:
    print(f"错误: {e}")
