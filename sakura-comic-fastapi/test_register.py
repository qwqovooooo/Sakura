import requests
import json

# 测试注册功能
def test_register():
    url = "http://localhost:8000/auth/register"
    data = {
        "name": "testuser1",
        "password": "test123"
    }
    
    try:
        response = requests.post(url, json=data)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return response
    except Exception as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    print("Testing registration...")
    test_register()