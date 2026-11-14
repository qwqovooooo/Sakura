"""
获取八戒资源的所有类型
"""
import requests

url = "https://api.apibdzy.com/api.php/provide/vod/"
params = {'ac': 'list'}
headers = {'User-Agent': 'Mozilla/5.0'}

print("=" * 60)
print("获取八戒资源的类型列表")
print("=" * 60)

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()
    
    if 'class' in data:
        types = data['class']
        print(f"\n找到 {len(types)} 个类型:\n")
        for t in types:
            print(f"  type_id: {t['type_id']}, type_name: {t['type_name']}")
    else:
        print("\n未找到类型数据")
        
except Exception as e:
    print(f"\n错误: {e}")

print("\n" + "=" * 60)
