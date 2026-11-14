"""
更新数据库结构，添加 is_admin 和 created_at 字段
"""
import sqlite3
import sys
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "sakura.db"

def update_database():
    """更新数据库结构"""
    print("=" * 50)
    print("更新数据库结构")
    print("=" * 50)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查 is_admin 字段是否存在
        cursor.execute("PRAGMA table_info(sakura_user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\n当前表结构字段: {columns}")
        
        # 添加 is_admin 字段
        if 'is_admin' not in columns:
            print("\n添加 is_admin 字段...")
            cursor.execute("""
                ALTER TABLE sakura_user 
                ADD COLUMN is_admin BOOLEAN DEFAULT 0
            """)
            print("✅ is_admin 字段添加成功")
        else:
            print("\n✅ is_admin 字段已存在")
        
        # 添加 created_at 字段
        if 'created_at' not in columns:
            print("\n添加 created_at 字段...")
            cursor.execute("""
                ALTER TABLE sakura_user 
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            print("✅ created_at 字段添加成功")
        else:
            print("\n✅ created_at 字段已存在")
        
        # 提交更改
        conn.commit()
        
        # 再次查看表结构
        cursor.execute("PRAGMA table_info(sakura_user)")
        columns_after = cursor.fetchall()
        
        print("\n更新后的表结构:")
        for col in columns_after:
            print(f"  - {col[1]}: {col[2]} (默认值: {col[4]})")
        
        print("\n✅ 数据库更新成功！")
        print("\n现在可以运行 create_default_admin.py 创建管理员账号了")
        
    except Exception as e:
        print(f"\n❌ 数据库更新失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_database()
