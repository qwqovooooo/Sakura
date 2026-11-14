"""
测试电影列表接口
"""
import asyncio
from app.config import AsyncSessionLocal
from app.models.models import MovDetail
from sqlalchemy.future import select
from sqlalchemy import desc

async def test_vod_list():
    async with AsyncSessionLocal() as db:
        # 测试查询
        query = select(MovDetail).order_by(desc(MovDetail.vod_time)).limit(12)
        
        result = await db.execute(query)
        movies = result.scalars().all()
        
        print(f"查询结果:")
        print(f"   找到 {len(movies)} 部电影")
        
        if movies:
            print(f"\n前5部电影:")
            for i, mov in enumerate(movies[:5], 1):
                print(f"\n{i}. {mov.vod_name}")
                print(f"   vod_id: {mov.vod_id}")
                print(f"   type_id: {mov.type_id}")
                print(f"   type_name: {mov.type_name}")
                print(f"   vod_pic: {'有' if mov.vod_pic else '无'}")
        else:
            print("\n 没有找到任何电影！")
            
            # 检查数据库中是否有数据
            count_query = select(MovDetail)
            count_result = await db.execute(count_query)
            all_movies = count_result.scalars().all()
            print(f"\n数据库中总共有 {len(all_movies)} 部电影")

if __name__ == "__main__":
    asyncio.run(test_vod_list())
