"""
重新运行爬虫，确保封面数据被保存
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.task.tasks import SakuraData

def main():
    print("=" * 60)
    print("重新爬取数据（包含封面）")
    print("=" * 60)
    
    sd = SakuraData()
    
    # 爬取第1页测试
    print(f"\n正在爬取第 1 页...")
    try:
        sd.get_mov_detail(1)
        print(f"✓ 第 1 页爬取完成")
    except Exception as e:
        print(f"× 第 1 页爬取失败: {e}")
    
    print("\n" + "=" * 60)
    print("完成！请检查数据库")
    print("=" * 60)

if __name__ == '__main__':
    main()
