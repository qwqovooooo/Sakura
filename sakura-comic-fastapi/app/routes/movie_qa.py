"""
电影问答模块 - 基于LLM的电影详情问答功能
功能：用户针对当前电影提问，LLM基于电影信息回答问题
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import json

from ..config import AsyncSessionLocal
from ..models.models import MovDetail

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


# ==================== 请求/响应模型 ====================

class MovieQARequest(BaseModel):
    """电影问答请求模型"""
    vod_id: int = Field(..., description="视频ID")
    question: str = Field(..., description="用户的问题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vod_id": 1,
                "question": "这部电影的主演是谁？"
            }
        }


class MovieQAResponse(BaseModel):
    """电影问答响应模型"""
    success: bool = Field(..., description="是否成功")
    answer: Optional[str] = Field(None, description="回答内容")
    movie_info: Optional[Dict[str, Any]] = Field(None, description="电影基本信息")
    error: Optional[str] = Field(None, description="错误信息")


# ==================== 数据库依赖 ====================

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# ==================== 电影问答Agent ====================

class MovieQAAgent:
    """电影问答助手"""
    
    def __init__(self, api_key: str = "sk-vzqpwilooukhpgzwifjbvlpodtlakpcbmimubkhvnmnaexss"):
        """初始化问答Agent"""
        self.api_key = api_key
        self.api_base = "https://api.siliconflow.cn/v1"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
    
    async def get_movie_info(self, vod_id: int, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        获取电影详细信息
        
        Args:
            vod_id: 视频ID
            db: 数据库会话
            
        Returns:
            电影信息字典
        """
        try:
            result = await db.execute(
                select(MovDetail).where(MovDetail.vod_id == vod_id)
            )
            movie = result.scalar_one_or_none()
            
            if not movie:
                return None
            
            return {
                "vod_id": movie.vod_id,
                "vod_name": movie.vod_name,
                "type_name": movie.type_name,
                "vod_actor": movie.vod_actor,
                "vod_director": movie.vod_director,
                "vod_area": movie.vod_area,
                "vod_year": movie.vod_year,
                "vod_content": movie.vod_content,
                "vod_score": movie.vod_score,
                "vod_remarks": movie.vod_remarks,
                "vod_class": movie.vod_class
            }
            
        except Exception as e:
            logger.error(f"获取电影信息失败: {str(e)}")
            raise
    
    async def search_web_info(self, movie_name: str, question: str) -> str:
        """
        从网络搜索电影相关信息
        
        Args:
            movie_name: 电影名称
            question: 用户问题
            
        Returns:
            搜索到的相关信息
        """
        try:
            # 使用百度搜索API或其他搜索引擎
            search_query = f"{movie_name} 剧情 简介 主演 导演"
            
            # 这里使用简单的HTTP请求获取搜索结果
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 使用DuckDuckGo搜索（免费，无需API Key）
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": search_query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 提取摘要信息
                    abstract = data.get('AbstractText', '')
                    if abstract:
                        return abstract
                    
                    # 如果没有摘要，尝试从相关主题获取
                    related_topics = data.get('RelatedTopics', [])
                    if related_topics and len(related_topics) > 0:
                        first_topic = related_topics[0]
                        if isinstance(first_topic, dict) and 'Text' in first_topic:
                            return first_topic['Text']
                
                return ""
                
        except Exception as e:
            logger.error(f"网络搜索失败: {str(e)}")
            return ""
    
    async def answer_question(
        self, 
        question: str, 
        movie_info: Dict[str, Any]
    ) -> str:
        """
        使用LLM回答关于电影的问题
        
        Args:
            question: 用户问题
            movie_info: 电影信息
            
        Returns:
            回答内容
        """
        # 构建电影信息文本
        movie_context = f"""
电影名称：{movie_info.get('vod_name', '未知')}
类型：{movie_info.get('type_name', '未知')}
主演：{movie_info.get('vod_actor', '未知')}
导演：{movie_info.get('vod_director', '未知')}
地区：{movie_info.get('vod_area', '未知')}
年份：{movie_info.get('vod_year', '未知')}
评分：{movie_info.get('vod_score', '未知')}
状态：{movie_info.get('vod_remarks', '未知')}
分类：{movie_info.get('vod_class', '未知')}
简介：{movie_info.get('vod_content', '暂无简介')}
        """.strip()
        
        # 如果简介为空或很短，尝试从网络搜索
        web_info = ""
        if not movie_info.get('vod_content') or len(movie_info.get('vod_content', '')) < 20:
            logger.info(f"简介信息不足，尝试网络搜索: {movie_info.get('vod_name')}")
            web_info = await self.search_web_info(movie_info.get('vod_name', ''), question)
            if web_info:
                movie_context += f"\n\n网络搜索信息：{web_info}"
        
        prompt = f"""你是一个友好的影视助手。用户正在观看一部影视作品，并向你提问。

影视作品信息：
{movie_context}

用户问题：{question}

请根据以上信息回答用户的问题。回答要求：

1. **优先使用已有信息回答**：如果信息中包含答案，请直接、简洁地回答
2. **信息不足时的处理**：
   - 如果问题是关于剧情/故事内容，但简介为空或不详细，请说："抱歉，暂时没有详细的剧情介绍。但根据片名和类型来看，这可能是一部[类型]作品。建议观看后再来交流！"
   - 如果问题是关于主演/导演等基本信息，但信息缺失，请说："暂时没有该信息的详细记录，建议查看视频播放页面或相关影评网站获取更多信息。"
3. **语气友好自然**：像朋友聊天一样，不要太生硬
4. **不编造信息**：只基于给定信息回答，不要虚构
5. **简洁明了**：控制在2-3句话以内

现在请回答用户的问题：
"""
        
        try:
            logger.info(f"调用LLM回答问题: {question}")
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data['choices'][0]['message']['content'].strip()
                    logger.info("LLM回答成功")
                    return answer
                else:
                    logger.error(f"LLM API错误: {response.status_code} {response.text}")
                    raise Exception(f"LLM API调用失败: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("LLM API超时")
            return "抱歉，回答超时了，请稍后再试。"
        except Exception as e:
            logger.error(f"LLM回答失败: {str(e)}")
            raise


# ==================== API 路由 ====================

@router.post("/ask", response_model=MovieQAResponse)
async def ask_about_movie(
    request: MovieQARequest,
    db: AsyncSession = Depends(get_db)
):
    """
    电影问答接口：针对特定电影回答用户问题
    
    支持的问题类型：
    - 主演是谁？
    - 导演是谁？
    - 这部电影讲的是什么？
    - 评分怎么样？
    - 是哪一年的作品？
    - 等等...
    """
    logger.info(f"收到电影问答请求 - vod_id: {request.vod_id}, question: {request.question}")
    
    try:
        # 创建问答Agent
        agent = MovieQAAgent()
        
        # 获取电影信息
        movie_info = await agent.get_movie_info(request.vod_id, db)
        
        if not movie_info:
            return MovieQAResponse(
                success=False,
                answer=None,
                movie_info=None,
                error="未找到该电影信息"
            )
        
        # 使用LLM回答问题
        answer = await agent.answer_question(request.question, movie_info)
        
        return MovieQAResponse(
            success=True,
            answer=answer,
            movie_info={
                "vod_id": movie_info["vod_id"],
                "vod_name": movie_info["vod_name"],
                "type_name": movie_info["type_name"]
            },
            error=None
        )
        
    except Exception as e:
        logger.error(f"电影问答失败: {str(e)}")
        return MovieQAResponse(
            success=False,
            answer=None,
            movie_info=None,
            error=f"问答失败: {str(e)}"
        )


@router.get("/suggestions/{vod_id}")
async def get_question_suggestions(vod_id: int):
    """
    获取建议的问题列表
    
    Args:
        vod_id: 视频ID
        
    Returns:
        建议问题列表
    """
    suggestions = [
        "这部电影的主演是谁？",
        "导演是谁？",
        "这部电影讲的是什么故事？",
        "评分怎么样？",
        "是哪一年的作品？",
        "属于什么类型？",
        "有哪些演员参演？",
        "电影的背景设定在哪里？"
    ]
    
    return {
        "success": True,
        "vod_id": vod_id,
        "suggestions": suggestions
    }
