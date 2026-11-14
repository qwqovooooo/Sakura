import requests
import json

# 测试推荐API
url = "http://127.0.0.1:8000/recommend/recommend"
data = {
    "description": "我想看一些轻松搞笑的电影",
    "limit": 5
}

response = requests.post(url, json=data)
print(f"状态码: {response.status_code}")
print(f"\n响应内容:")
result = response.json()
print(json.dumps(result, ensure_ascii=False, indent=2))

# 检查是否有SQL字段
if 'sql' in result:
    print(f"\n生成的SQL语句:")
    print(result['sql'])
else:
    print("\n警告: 响应中没有SQL字段!")
