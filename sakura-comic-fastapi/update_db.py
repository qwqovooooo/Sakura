"""
更新数据库表结构脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import AsyncSessionLocal
from sqlalchemy import text

async def update_database():
    """更新数据库表结构"""
    print("=" * 50)
    print("更新数据库表结构")
    print("=" * 50)
    
    try:
        async with AsyncSessionLocal() as session:
            # 检查字段是否已存在
            check_sql = """
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'movie' 
            AND TABLE_NAME = 'sakura_user' 
            AND COLUMN_NAME = 'is_admin'
            """
            result = await session.execute(text(check_sql))
            exists = result.scalar() > 0
            
            if not exists:
                print("\n正在添加 is_admin 字段...")
                await session.execute(text(
                    "ALTER TABLE sakura_user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE AFTER password_hash"
                ))
                print("✅ is_admin 字段添加成功")
            else:
                print("\n✓ is_admin 字段已存在")
            
            # 检查 created_at 字段
            check_sql2 = """
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'movie' 
            AND TABLE_NAME = 'sakura_user' 
            AND COLUMN_NAME = 'created_at'
            """
            result2 = await session.execute(text(check_sql2))
            exists2 = result2.scalar() > 0
            
            if not exists2:
                print("\n正在添加 created_at 字段...")
                await session.execute(text(
                    "ALTER TABLE sakura_user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER is_admin"
                ))
                print("✅ created_at 字段添加成功")
            else:
                print("\n✓ created_at 字段已存在")
            
            await session.commit()
            print("\n✅ 数据库表结构更新完成！")
            
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_database())
