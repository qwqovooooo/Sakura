import asyncio
from app.config import AsyncSessionLocal
from sqlalchemy import text

async def test():
    async with AsyncSessionLocal() as session:
        # 总数
        result = await session.execute(text('SELECT COUNT(*) as count FROM sakura_movdetail'))
        print(f'数据库总电影数: {result.scalar()}')
        
        # 测试喜剧
        result = await session.execute(text(
            "SELECT vod_name, vod_class, vod_score FROM sakura_movdetail WHERE vod_class LIKE '%喜剧%' LIMIT 5"
        ))
        rows = result.fetchall()
        print('\n喜剧类电影:')
        for r in rows:
            print(f'  {r[0]}, 类型:{r[1]}, 评分:{r[2]}')
        
        # 测试关键词查询（模拟当前的SQL）
        keywords = ['我想看一些轻松搞笑的电影，适合周末放松']
        keyword_conditions = " OR ".join([
            f"vod_name LIKE '%{kw}%' OR vod_content LIKE '%{kw}%'" 
            for kw in keywords[:3]
        ])
        sql = f"SELECT COUNT(*) FROM sakura_movdetail WHERE ({keyword_conditions})"
        print(f'\n测试SQL: {sql}')
        result = await session.execute(text(sql))
        count = result.scalar()
        print(f'查询结果数: {count}')
        
        # 测试改进的关键词分词
        keywords_new = ['轻松', '搞笑', '喜剧', '周末']
        keyword_conditions_new = " OR ".join([
            f"vod_name LIKE '%{kw}%' OR vod_content LIKE '%{kw}%' OR vod_class LIKE '%{kw}%'" 
            for kw in keywords_new
        ])
        sql_new = f"SELECT vod_name, vod_class FROM sakura_movdetail WHERE ({keyword_conditions_new}) LIMIT 5"
        print(f'\n改进后的SQL: {sql_new}')
        result = await session.execute(text(sql_new))
        rows = result.fetchall()
        print(f'查询到 {len(rows)} 部电影:')
        for r in rows:
            print(f'  {r[0]}, 类型:{r[1]}')

asyncio.run(test())
