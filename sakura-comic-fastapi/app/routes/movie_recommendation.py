"""
智能电影推荐模块 - Agentic Workflow
功能：用户输入一段话 -> LLM分析需求 -> 自主查询数据库 -> 返回推荐电影
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
import re
import httpx

from ..config import AsyncSessionLocal

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


# ==================== 请求/响应模型 ====================

class RecommendationRequest(BaseModel):
    """推荐请求模型"""
    description: str = Field(..., description="用户描述的观影需求")
    limit: Optional[int] = Field(10, description="推荐数量", ge=1, le=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "我想看一些轻松搞笑的电影，适合周末放松",
                "limit": 10
            }
        }


class MovieRecommendation(BaseModel):
    """推荐电影模型"""
    vod_id: int
    vod_name: str
    vod_score: Optional[str]
    vod_year: Optional[str]
    vod_class: Optional[str]
    vod_area: Optional[str]
    vod_actor: Optional[str]
    vod_director: Optional[str]
    vod_pic: Optional[str]
    vod_content: Optional[str]
    reason: Optional[str] = Field(None, description="推荐理由")


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    success: bool
    analysis: Optional[str] = Field(None, description="需求分析")
    query_strategy: Optional[str] = Field(None, description="查询策略")
    sql: Optional[str] = Field(None, description="生成的SQL语句")
    movies: Optional[List[MovieRecommendation]] = Field(None, description="推荐电影列表")
    error: Optional[str] = None


# ==================== 数据库依赖 ====================

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# ==================== Agent 核心类 ====================

class MovieRecommendationAgent:
    """电影推荐智能代理"""
    
    # 数据库表结构
    SCHEMA_INFO = """
    sakura_movdetail (电影详情表):
        - vod_id: 视频ID (主键)
        - vod_name: 电影名称
        - type_name: 类型 (如: 电影、电视剧、动漫、综艺)
        - vod_class: 分类标签 (如: 喜剧、动作、爱情、科幻等)
        - vod_actor: 演员列表
        - vod_director: 导演
        - vod_area: 地区 (如: 大陆、美国、日本等)
        - vod_year: 年份
        - vod_score: 评分 (字符串类型, 需转换)
        - vod_content: 剧情简介
        - vod_pic: 封面图
        - vod_hits: 点击量
        - vod_time: 更新时间
    """
    
    def __init__(self):
        """初始化推荐代理"""
        self.api_key = "sk-vzqpwilooukhpgzwifjbvlpodtlakpcbmimubkhvnmnaexss"
        self.api_base = "https://api.siliconflow.cn/v1"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
    
    async def _analyze_user_intent(self, description: str) -> Dict[str, Any]:
        """
        第一步：分析用户意图
        
        Args:
            description: 用户描述
            
        Returns:
            分析结果，包含提取的关键信息
        """
        prompt = f"""你是一个专业的电影推荐助手。请分析用户的观影需求，提取关键信息。

用户描述：{description}

请从以下维度分析：
1. **情绪/氛围**：用户想要什么样的观影体验？(如：轻松、紧张、感动、刺激等)
2. **类型偏好**：偏好什么类型？(如：喜剧、动作、爱情、科幻、悬疑、恐怖、动漫等)
3. **时代/年份**：有年代要求吗？(如：经典老片、近期新片、特定年份)
4. **地区**：有地区偏好吗？(如：国产、欧美、日韩等)
5. **演员/导演**：提到特定演员或导演吗？
6. **其他特征**：评分、时长、剧情元素等

请以JSON格式返回分析结果：
{{
    "keywords": ["关键词1", "关键词2", ...],  // 提取的核心关键词
    "mood": "情绪描述",
    "genres": ["类型1", "类型2", ...],  // 可能的类型
    "time_period": "时间要求",  // 如 "近期"、"经典"、"2020年后" 等
    "region": "地区偏好",  // 如 "大陆"、"美国"、"日本" 等
    "people": ["人名1", "人名2", ...],  // 演员或导演
    "other_requirements": "其他要求",
    "summary": "需求总结"  // 一句话总结用户需求
}}

只返回JSON，不要其他内容。"""

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'].strip()
                    
                    # 清理JSON
                    content = re.sub(r'```json\s*', '', content)
                    content = re.sub(r'```\s*$', '', content)
                    content = content.strip()
                    
                    result = json.loads(content)
                    logger.info(f"Intent analysis result: {result}")
                    return result
                else:
                    raise Exception(f"API failed with status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            # 降级：简单关键词提取
            return {
                "keywords": description.split()[:5],
                "summary": description,
                "genres": [],
                "mood": "未知",
                "time_period": "",
                "region": "",
                "people": [],
                "other_requirements": ""
            }
    
    async def _generate_query_strategy(
        self, 
        intent: Dict[str, Any],
        limit: int
    ) -> Dict[str, str]:
        """
        第二步：根据意图生成查询策略
        
        Args:
            intent: 用户意图分析结果
            limit: 推荐数量
            
        Returns:
            包含SQL和策略说明
        """
        prompt = f"""你是数据库查询专家。根据用户的观影需求，生成最合适的SQL查询语句。

数据库表结构：
{self.SCHEMA_INFO}

用户需求分析结果：
{json.dumps(intent, ensure_ascii=False, indent=2)}

推荐数量：{limit}

请生成SQL查询，遵循以下规则：
1. **必须包含字段**：vod_id, vod_name, vod_score, vod_year, vod_class, vod_area, vod_actor, vod_director, vod_pic, vod_content
2. 使用 LIKE 进行模糊匹配
3. **重要**：使用 OR 连接多个条件，而不是 AND，让查询结果更多
4. 优先考虑评分高、点击量高的影片
5. 合理使用 ORDER BY 排序
6. 使用 LIMIT {limit}

生成策略示例：
- 如果用户要轻松搞笑 → (vod_class LIKE '%喜剧%' OR vod_content LIKE '%搞笑%' OR vod_content LIKE '%轻松%')
- 如果要经典老片 → vod_year < '2010' OR vod_score > '7.0'
- 如果要美国大片 → vod_area LIKE '%美国%'
- 如果提到演员 → vod_actor LIKE '%演员名%'

**注意：不要使用过多 AND 条件，否则可能查不到结果！**

请以JSON格式返回：
{{
    "sql": "完整的SELECT语句",
    "strategy": "查询策略说明"
}}

只返回JSON，不要其他内容。
"""
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 600
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'].strip()
                    
                    content = re.sub(r'```json\s*', '', content)
                    content = re.sub(r'```\s*$', '', content)
                    content = content.strip()
                    
                    result = json.loads(content)
                    logger.info(f"Query strategy: {result}")
                    return result
                else:
                    raise Exception(f"API failed with status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Query generation error: {str(e)}")
            # 降级：基于关键词的简单查询
            return self._generate_query_with_rules(intent, limit)
    
    def _generate_query_with_rules(
        self,
        intent: Dict[str, Any],
        limit: int
    ) -> Dict[str, str]:
        """
        基于规则生成SQL查询（快速模式）
        
        Args:
            intent: 用户意图
            limit: 限制数量
            
        Returns:
            SQL和策略说明
        """
        keywords = intent.get('keywords', [])
        genres = intent.get('genres', [])
        
        conditions = []
        
        # 优先使用类型查询
        if genres:
            genre_conditions = " OR ".join([f"vod_class LIKE '%{g}%'" for g in genres[:3]])
            conditions.append(f"({genre_conditions})")
        
        # 其次使用关键词查询
        if keywords:
            keyword_conditions = " OR ".join([
                f"vod_name LIKE '%{kw}%' OR vod_content LIKE '%{kw}%'" 
                for kw in keywords[:3]
            ])
            if keyword_conditions:
                conditions.append(f"({keyword_conditions})")
        
        # 如果没有任何条件，返回高分电影
        if not conditions:
            where_clause = "vod_score IS NOT NULL AND vod_score != ''"
        else:
            # 使用 OR 连接，而不是 AND，让查询更宽松
            where_clause = " OR ".join(conditions)
        
        sql = f"""
SELECT vod_id, vod_name, vod_score, vod_year, vod_class, vod_area, 
       vod_actor, vod_director, vod_pic, vod_content
FROM sakura_movdetail
WHERE {where_clause}
ORDER BY 
    CASE WHEN vod_score IS NOT NULL AND vod_score != '' 
         THEN CAST(vod_score AS DECIMAL(3,1)) 
         ELSE 0 END DESC,
    vod_hits DESC
LIMIT {limit}
        """.strip()
        
        return {
            "sql": sql,
            "strategy": f"根据关键词 {', '.join(keywords[:3]) if keywords else '无'} 和类型 {', '.join(genres[:3]) if genres else '无'} 查询"
        }
    
    async def _execute_query(
        self, 
        sql: str, 
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        第三步：执行数据库查询
        
        Args:
            sql: SQL语句
            db: 数据库会话
            
        Returns:
            查询结果列表
        """
        try:
            # 安全检查
            if not sql.strip().upper().startswith('SELECT'):
                raise Exception("只允许SELECT查询")
            
            result = await db.execute(text(sql))
            rows = result.fetchall()
            
            if rows:
                columns = result.keys()
                result_list = [dict(zip(columns, row)) for row in rows]
                
                # 处理datetime类型
                for item in result_list:
                    for key, value in item.items():
                        if hasattr(value, 'isoformat'):
                            item[key] = value.isoformat()
                
                return result_list
            else:
                return []
                
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    async def _generate_recommendations(
        self,
        movies: List[Dict[str, Any]],
        intent: Dict[str, Any]
    ) -> List[MovieRecommendation]:
        """
        第四步：为每部电影生成推荐理由（可选）
        
        Args:
            movies: 查询到的电影列表
            intent: 用户意图
            
        Returns:
            带推荐理由的电影列表
        """
        # 简化版：基于规则生成推荐理由
        recommendations = []
        
        for movie in movies:
            reason_parts = []
            
            # 基于评分
            score = movie.get('vod_score')
            if score and score != '' and float(score) >= 8.0:
                reason_parts.append(f"高分佳作({score}分)")
            
            # 基于类型匹配
            genres = intent.get('genres', [])
            vod_class = movie.get('vod_class', '')
            matched_genres = [g for g in genres if g in vod_class]
            if matched_genres:
                reason_parts.append(f"符合{'/'.join(matched_genres)}类型")
            
            # 基于关键词匹配
            keywords = intent.get('keywords', [])
            content = movie.get('vod_content', '')
            matched_kw = [kw for kw in keywords if kw in content or kw in movie.get('vod_name', '')]
            if matched_kw:
                reason_parts.append(f"匹配关键词: {', '.join(matched_kw[:2])}")
            
            # 基于情绪匹配
            mood = intent.get('mood', '')
            if mood and mood in content:
                reason_parts.append(f"符合{mood}氛围")
            
            reason = "、".join(reason_parts) if reason_parts else "符合您的观影需求"
            
            recommendations.append(MovieRecommendation(
                vod_id=movie.get('vod_id'),
                vod_name=movie.get('vod_name'),
                vod_score=movie.get('vod_score'),
                vod_year=movie.get('vod_year'),
                vod_class=movie.get('vod_class'),
                vod_area=movie.get('vod_area'),
                vod_actor=movie.get('vod_actor'),
                vod_director=movie.get('vod_director'),
                vod_pic=movie.get('vod_pic'),
                vod_content=movie.get('vod_content'),
                reason=reason
            ))
        
        return recommendations
    
    def _extract_chinese_keywords(self, description: str) -> list:
        """
        从中文描述中提取关键词
        
        Args:
            description: 用户输入的描述
            
        Returns:
            关键词列表
        """
        # 常见的电影类型关键词
        genre_keywords = [
            '喜剧', '动作', '爱情', '科幻', '恐怖', '惊悚', '悬疑', '剧情', 
            '战争', '动画', '纪录片', '奇幻', '冒险', '犯罪', '历史', '武侠',
            '搞笑', '感人', '治愈', '烧脑', '高分', '经典'
        ]
        
        # 常见的情绪/氛围关键词
        mood_keywords = [
            '轻松', '放松', '刺激', '紧张', '感动', '温馨', '浪漫', '热血',
            '搞笑', '幽默', '深刻', '震撼', '催泪', '治愈', '快乐', '悲伤'
        ]
        
        # 地区关键词
        region_keywords = [
            '欧美', '美国', '英国', '法国', '日本', '韩国', '中国', '香港', 
            '台湾', '国产', '好莱坞', '迪士尼'
        ]
        
        # 时间关键词
        time_keywords = [
            '最近', '新片', '老片', '经典', '90年代', '80年代', '2000年',
            '近期', '上映', '新上映'
        ]
        
        keywords = []
        
        # 提取类型关键词
        for keyword in genre_keywords:
            if keyword in description and keyword not in keywords:
                keywords.append(keyword)
        
        # 提取情绪关键词
        for keyword in mood_keywords:
            if keyword in description and keyword not in keywords:
                keywords.append(keyword)
        
        # 提取地区关键词
        for keyword in region_keywords:
            if keyword in description and keyword not in keywords:
                keywords.append(keyword)
        
        # 提取时间关键词
        for keyword in time_keywords:
            if keyword in description and keyword not in keywords:
                keywords.append(keyword)
        
        # 如果没有提取到任何关键词，尝试简单的字符串分割
        if not keywords:
            # 移除常见的无意义词
            stop_words = ['我', '想', '看', '一些', '的', '电影', '吗', '有', '什么', '推荐', '给', '几部', '适合', '周末']
            words = []
            for word in description:
                if len(word) > 1 and word not in stop_words:
                    words.append(word)
            keywords = words[:5] if words else ['高分']  # 如果还是没有，默认搜索高分电影
        
        return keywords[:5]  # 最多返回5个关键词
    
    async def recommend_movies(
        self,
        description: str,
        limit: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        完整的推荐流程（Agentic Workflow）
        
        Args:
            description: 用户描述
            limit: 推荐数量
            db: 数据库会话
            
        Returns:
            推荐结果
        """
        try:
            logger.info(f"Starting recommendation for: {description}")
            
            # 优化：直接使用规则引擎，跳过LLM调用，加快速度
            # Step 1: 提取中文关键词
            logger.info("Step 1: Extracting keywords...")
            keywords = self._extract_chinese_keywords(description)
            intent = {
                'keywords': keywords,
                'summary': description,
                'genres': [],
                'mood': '',
                'time_period': '',
                'region': '',
                'people': [],
                'other_requirements': ''
            }
            
            # Step 2: 直接使用规则生成SQL
            logger.info("Step 2: Generating query with rules...")
            query_info = self._generate_query_with_rules(intent, limit)
            
            # Step 3: 执行查询
            logger.info("Step 3: Executing query...")
            movies = await self._execute_query(query_info['sql'], db)
            
            # Step 4: 生成推荐理由
            logger.info("Step 4: Generating recommendations...")
            recommendations = await self._generate_recommendations(movies, intent)
            
            result = {
                "success": True,
                "analysis": f"根据您的描述：{description}",
                "query_strategy": query_info['strategy'],
                "sql": query_info['sql'],  # 添加SQL语句
                "movies": recommendations,
                "error": None
            }
            logger.info(f"返回结果包含SQL: {'sql' in result}, SQL内容: {result.get('sql', 'None')[:100] if result.get('sql') else 'None'}")
            return result
            
        except Exception as e:
            logger.error(f"Recommendation error: {str(e)}")
            return {
                "success": False,
                "analysis": None,
                "query_strategy": None,
                "sql": None,
                "movies": None,
                "error": f"推荐失败: {str(e)}"
            }


# ==================== API 路由 ====================

@router.post("/recommend", response_model=RecommendationResponse)
async def get_movie_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    智能电影推荐接口
    
    用户输入一段话描述观影需求，AI自动分析并推荐电影
    
    示例：
    - "我想看一些轻松搞笑的电影，适合周末放松"
    - "推荐几部高分悬疑片，最好是欧美的"
    - "想看周星驰的喜剧电影"
    - "有什么感人的爱情电影吗？"
    - "推荐一些科幻大片，特效要好"
    """
    logger.info(f"Received recommendation request: {request.description}")
    
    # 创建推荐代理
    agent = MovieRecommendationAgent()
    
    # 执行推荐流程
    result = await agent.recommend_movies(
        request.description,
        request.limit,
        db
    )
    
    # 调试：检查result中resql字段
    logger.info(f"API endpoint - result keys: {result.keys()}")
    logger.info(f"API endpoint - 'sql' in result: {'sql' in result}")
    if 'sql' in result:
        logger.info(f"API endpoint - SQL content: {result['sql'][:100]}")
    
    # 直接返回字典，让FastAPI自动序列化
    return result


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "message": "Movie Recommendation Service is running",
        "version": "1.0.0"
    }


@router.get("/test-sql")
async def test_sql():
    """测试SQL字段返回"""
    return {
        "success": True,
        "sql": "SELECT * FROM test",
        "message": "Test SQL field"
    }
