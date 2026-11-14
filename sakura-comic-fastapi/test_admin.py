"""
测试管理后台功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """测试管理员登录"""
    print("=" * 50)
    print("1. 测试管理员登录")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    data = {"name": "admin", "password": "admin123"}
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        token = result["data"]["token"]
        # 将 jwt 前缀改为 Bearer
        if token.startswith("jwt "):
            token = "Bearer " + token[4:]
        print(f"\n✅ 登录成功！Token: {token[:50]}...")
        return token
    else:
        print("\n❌ 登录失败")
        return None

def test_get_users(token):
    """测试获取用户列表"""
    print("\n" + "=" * 50)
    print("2. 测试获取用户列表")
    print("=" * 50)
    
    url = f"{BASE_URL}/admin/users?page=1&page_size=5"
    # 修正 Token 格式，已经包含 jwt 前缀
    headers = {"Authorization": token}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ 获取成功！共 {result['data']['data']['total']} 个用户")
    else:
        print("\n❌ 获取失败")

def test_get_movies(token):
    """测试获取电影列表"""
    print("\n" + "=" * 50)
    print("3. 测试获取电影列表")
    print("=" * 50)
    
    url = f"{BASE_URL}/admin/movies?page=1&page_size=5"
    headers = {"Authorization": token}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"✅ 获取成功！共 {result['data']['data']['total']} 部电影")
        print(f"前5部电影:")
        for movie in result['data']['data']['list'][:5]:
            print(f"  - {movie['vod_name']} ({movie['vod_year']})")
    else:
        print(f"\n❌ 获取失败: {result}")

def test_get_comments(token):
    """测试获取评论列表"""
    print("\n" + "=" * 50)
    print("4. 测试获取评论列表")
    print("=" * 50)
    
    url = f"{BASE_URL}/admin/comments?page=1&page_size=5"
    headers = {"Authorization": token}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"✅ 获取成功！共 {result['data']['data']['total']} 条评论")
        print(f"最近5条评论:")
        for comment in result['data']['data']['list'][:5]:
            print(f"  - {comment['user_name']}: {comment['body'][:30]}...")
    else:
        print(f"\n❌ 获取失败: {result}")

def main():
    print("\n🚀 开始测试管理后台功能...\n")
    
    # 1. 登录获取 Token
    token = test_admin_login()
    if not token:
        print("\n⚠️  登录失败，无法继续测试")
        return
    
    # 2. 测试用户管理
    test_get_users(token)
    
    # 3. 测试电影管理
    test_get_movies(token)
    
    # 4. 测试评论管理
    test_get_comments(token)
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
    print("\n💡 提示：")
    print("  - 访问 http://localhost:8000/docs 查看完整 API 文档")
    print("  - 管理员账号: admin / admin123")
    print("  - 所有管理接口都在 /admin 路径下")

if __name__ == "__main__":
    main()
