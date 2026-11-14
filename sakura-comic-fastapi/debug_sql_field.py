import asyncio
from app.routes.movie_recommendation import MovieRecommendationAgent, RecommendationResponse
from app.config import AsyncSessionLocal

async def test():
    agent = MovieRecommendationAgent()
    
    async with AsyncSessionLocal() as db:
        result = await agent.recommend_movies(
            description="我想看一些轻松搞笑的电影",
            limit=5,
            db=db
        )
        
        print(f"返回的字典类型: {type(result)}")
        print(f"字典的keys: {result.keys()}")
        print(f"是否包含sql: {'sql' in result}")
        print(f"\nSQL内容:")
        print(result.get('sql', 'None'))
        
        # 测试 Pydantic 模型
        print(f"\n使用 Pydantic 模型:")
        response = RecommendationResponse(**result)
        print(f"response.sql = {response.sql}")
        
        # 转换成字典
        response_dict = response.model_dump()
        print(f"\nmodel_dump() 后的keys: {response_dict.keys()}")
        print(f"model_dump() 是否包含sql: {'sql' in response_dict}")

asyncio.run(test())
