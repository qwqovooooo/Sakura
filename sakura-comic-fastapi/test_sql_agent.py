"""
测试 SQL Agent 智能搜索功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_sql_agent():
    """测试SQL Agent接口"""
    
    print("=" * 60)
    print("测试 SQL Agent 智能搜索功能")
    print("=" * 60)
    
    # 测试问题列表
    test_questions = [
        "查询评分最高的5部电影",
        "最新的10部电影",
        "点击量最高的电影",
        "用户总数是多少",
        "统计各类型电影数量",
        "最新的20条评论"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【测试 {i}】问题: {question}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/sql-agent/ask",
                json={"question": question},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✓ 成功")
                print(f"SQL: {data.get('sql', 'N/A')}")
                print(f"说明: {data.get('explanation', 'N/A')}")
                
                result = data.get('result', [])
                if result:
                    print(f"结果数量: {len(result)}")
                    print(f"结果示例: {json.dumps(result[0] if len(result) > 0 else {}, ensure_ascii=False, indent=2)}")
                else:
                    print("结果: 无数据")
            else:
                print(f"✗ 失败 - HTTP {response.status_code}")
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
    
    # 测试获取示例问题
    print("\n" + "=" * 60)
    print("获取示例问题")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/sql-agent/examples")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"✗ 失败 - HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
    
    # 测试获取数据库结构
    print("\n" + "=" * 60)
    print("获取数据库结构")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/sql-agent/schema")
        if response.status_code == 200:
            data = response.json()
            print("✓ 成功获取数据库结构信息")
        else:
            print(f"✗ 失败 - HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {str(e)}")


if __name__ == "__main__":
    print("\n请确保后端服务已启动 (http://localhost:8000)")
    input("按 Enter 键开始测试...")
    test_sql_agent()
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
