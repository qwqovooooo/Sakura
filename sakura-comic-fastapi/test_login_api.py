import requests
import json

# 测试登录接口
url = "http://localhost:8000/auth/login"
data = {
    "name": "admin",
    "password": "admin123"
}

print(f"🔍 测试登录接口: {url}")
print(f"📤 请求数据: {json.dumps(data, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data)
    print(f"✅ 状态码: {response.status_code}")
    print(f"📥 响应数据:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ 错误: {e}")
