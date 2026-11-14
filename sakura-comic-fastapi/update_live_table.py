"""
更新直播间表，添加外部直播源字段
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sakura.db"

def update_live_room_table():
    """更新直播间表结构"""
    print("=" * 50)
    print("更新直播间表 - 添加外部直播源支持")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(live_rooms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加 source_type 字段
        if 'source_type' not in columns:
            print("\n添加 source_type 字段...")
            cursor.execute("""
                ALTER TABLE live_rooms 
                ADD COLUMN source_type VARCHAR(20) DEFAULT 'self'
            """)
            print("✅ source_type 字段添加成功")
        else:
            print("\n✅ source_type 字段已存在")
        
        # 添加 source_url 字段
        if 'source_url' not in columns:
            print("\n添加 source_url 字段...")
            cursor.execute("""
                ALTER TABLE live_rooms 
                ADD COLUMN source_url VARCHAR(500)
            """)
            print("✅ source_url 字段添加成功")
        else:
            print("\n✅ source_url 字段已存在")
        
        conn.commit()
        
        # 查看更新后的表结构
        cursor.execute("PRAGMA table_info(live_rooms)")
        columns_after = cursor.fetchall()
        
        print("\n更新后的表结构:")
        for col in columns_after:
            print(f"  - {col[1]}: {col[2]}")
        
        print("\n✅ 数据库更新完成！")
        print("\n现在支持以下功能：")
        print("  1. 自己推流直播 (source_type='self')")
        print("  2. 嵌入外部直播 (source_type='external')")
        
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_live_room_table()
