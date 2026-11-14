import asyncio
from sqlalchemy import text
from app.config import AsyncSessionLocal

async def add_indexes():
    """为常用查询字段添加索引，提升查询速度"""
    async with AsyncSessionLocal() as db:
        indexes = [
            ("idx_type_id", "CREATE INDEX idx_type_id ON sakura_movdetail(type_id)"),
            ("idx_vod_time", "CREATE INDEX idx_vod_time ON sakura_movdetail(vod_time)"),
            ("idx_vod_name", "CREATE INDEX idx_vod_name ON sakura_movdetail(vod_name)"),
            ("idx_type_name", "CREATE INDEX idx_type_name ON sakura_movdetail(type_name)"),
            ("idx_vod_area", "CREATE INDEX idx_vod_area ON sakura_movdetail(vod_area)"),
            ("idx_vod_year", "CREATE INDEX idx_vod_year ON sakura_movdetail(vod_year)"),
            ("idx_type_time", "CREATE INDEX idx_type_time ON sakura_movdetail(type_id, vod_time)"),
        ]
        
        
        for idx_name, create_sql in indexes:
            try:
                await db.execute(text(create_sql))
                print(f"索引 {idx_name} 添加成功")
            except Exception as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print(f"索引 {idx_name} 已存在，跳过")
                else:
                    print(f"索引 {idx_name} 添加失败: {e}")
        
        try:
            await db.commit()
            print("\n 所有索引处理完成！查询速度将大幅提升")
        except Exception as e:
            print(f"\n 提交失败: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(add_indexes())
