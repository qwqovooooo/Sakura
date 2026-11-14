import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.task.tasks import SakuraData

def main():
    print("=" * 60)
    print("开始爬取樱花动漫数据")
    print("=" * 60)
    
    sd = SakuraData()
    
    # 爬取前200页，获取更多数据
    for i in range(1, 201):
        print(f"\n正在爬取第 {i} 页...")
        try:
            sd.get_mov_detail(i)
            print(f"✓ 第 {i} 页爬取完成")
        except Exception as e:
            print(f"× 第 {i} 页爬取失败: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("数据爬取完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()