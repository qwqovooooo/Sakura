"""
SQL Agent 智能搜索模块
功能：接收用户自然语言问题 -> 生成SQL语句 -> 执行查询 -> 返回结果
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
import re
import httpx
import os

from ..config import AsyncSessionLocal

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


# ==================== 请求/响应模型 ====================

class QuestionRequest(BaseModel):
    """用户问题请求模型"""
    question: str = Field(..., description="用户的自然语言问题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "查询评分最高的5部电影"
            }
        }


class SQLResponse(BaseModel):
    """SQL生成响应模型"""
    success: bool = Field(..., description="是否成功")
    sql: Optional[str] = Field(None, description="生成的SQL语句")
    result: Optional[List[Dict[str, Any]]] = Field(None, description="查询结果")
    error: Optional[str] = Field(None, description="错误信息")
    explanation: Optional[str] = Field(None, description="SQL解释说明")


# ==================== 数据库依赖 ====================

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# ==================== SQL Agent 核心类 ====================

class SQLAgent:
    """SQL Agent 智能查询助手"""
    
    # 数据库表结构描述
    SCHEMA_INFO = """
    数据库包含以下表结构：
    
    1. sakura_movtype (电影类型表)
       - type_id: 类型ID (主键)
       - type_name: 类型名称
    
    2. sakura_movinfo (电影信息表)
       - id: 自增ID (主键)
       - type_id: 类型ID (外键)
       - type_name: 类型名称
       - vod_en: 英文名
       - vod_id: 视频ID (唯一)
       - vod_name: 视频名称
       - vod_play_from: 播放来源
       - vod_remarks: 备注
       - vod_time: 更新时间
    
    3. sakura_movdetail (电影详情表)
       - id: 自增ID (主键)
       - vod_id: 视频ID (唯一)
       - vod_name: 视频名称
       - type_id: 类型ID (外键)
       - type_name: 类型名称
       - vod_actor: 演员
       - vod_director: 导演
       - vod_area: 地区
       - vod_year: 年份
       - vod_content: 简介
       - vod_score: 评分
       - vod_remarks: 备注
       - vod_pic: 封面图
       - vod_play_url: 播放地址
       - vod_hits: 总点击量
       - vod_time: 更新时间
    
    4. sakura_user (用户表)
       - id: 用户ID (主键)
       - name: 用户名 (唯一)
       - password_hash: 密码哈希
       - is_admin: 是否管理员
       - created_at: 创建时间
    
    5. sakura_comment (评论表)
       - id: 评论ID (主键)
       - body: 评论内容
       - reviewed: 是否审核通过
       - timestamp: 评论时间
       - user_id: 用户ID (外键)
       - movdetail_id: 电影详情ID (外键)
       - replied_id: 回复的评论ID (外键，自关联)
    
    6. sakura_user_collection (用户收藏表)
       - id: 收藏ID (主键)
       - user_id: 用户ID (外键)
       - movdetail_id_list: 收藏的电影ID列表 (文本格式，分号分隔)
    """
    
    def __init__(self, api_key: str = "sk-vzqpwilooukhpgzwifjbvlpodtlakpcbmimubkhvnmnaexss"):
        """初始化SQL Agent"""
        self.api_key = api_key
        self.api_base = "https://api.siliconflow.cn/v1"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
    
    def _generate_sql_with_rules(self, question: str) -> Dict[str, str]:
        """
        基于规则的SQL生成（简化版，不依赖外部LLM）
        
        Args:
            question: 用户问题
            
        Returns:
            包含sql和explanation的字典
        """
        question_lower = question.lower()
        
        # 规则1: 查询电影列表
        if any(keyword in question_lower for keyword in ['电影', '视频', 'movie', 'vod']):
            if '评分' in question_lower or 'score' in question_lower:
                if '最高' in question_lower or 'top' in question_lower or '前' in question_lower:
                    # 提取数字
                    num_match = re.search(r'(\d+)', question)
                    limit = num_match.group(1) if num_match else '5'
                    
                    sql = f"""
SELECT vod_id, vod_name, vod_score, vod_year, vod_area, vod_actor, vod_director
FROM sakura_movdetail
WHERE vod_score IS NOT NULL AND vod_score != ''
ORDER BY CAST(vod_score AS DECIMAL(3,1)) DESC
LIMIT {limit}
                    """.strip()
                    explanation = f"查询评分最高的{limit}部电影，按评分降序排列"
                    return {"sql": sql, "explanation": explanation}
            
            if '点击' in question_lower or 'hits' in question_lower or '热门' in question_lower:
                num_match = re.search(r'(\d+)', question)
                limit = num_match.group(1) if num_match else '10'
                
                sql = f"""
SELECT vod_id, vod_name, vod_hits, vod_score, vod_year
FROM sakura_movdetail
WHERE vod_hits IS NOT NULL
ORDER BY vod_hits DESC
LIMIT {limit}
                """.strip()
                explanation = f"查询点击量最高的{limit}部电影"
                return {"sql": sql, "explanation": explanation}
            
            if '最新' in question_lower or 'latest' in question_lower or '新' in question_lower:
                num_match = re.search(r'(\d+)', question)
                limit = num_match.group(1) if num_match else '10'
                
                sql = f"""
SELECT vod_id, vod_name, vod_time, vod_year, vod_score
FROM sakura_movdetail
WHERE vod_time IS NOT NULL
ORDER BY vod_time DESC
LIMIT {limit}
                """.strip()
                explanation = f"查询最新更新的{limit}部电影"
                return {"sql": sql, "explanation": explanation}
            
            # 类型查询
            for type_keyword in ['动漫', '电影', '电视剧', '综艺']:
                if type_keyword in question:
                    num_match = re.search(r'(\d+)', question)
                    limit = num_match.group(1) if num_match else '10'
                    
                    sql = f"""
SELECT vod_id, vod_name, vod_score, vod_year, type_name
FROM sakura_movdetail
WHERE type_name LIKE '%{type_keyword}%'
ORDER BY vod_time DESC
LIMIT {limit}
                    """.strip()
                    explanation = f"查询{type_keyword}类型的{limit}部作品"
                    return {"sql": sql, "explanation": explanation}
            
            # 演员/导演查询
            if '演员' in question_lower or 'actor' in question_lower:
                # 提取演员名（简单实现，假设名字在问号前）
                name_match = re.search(r'演员.*?([^\s，。？！,?!]+)', question)
                if name_match:
                    actor_name = name_match.group(1)
                    sql = f"""
SELECT vod_id, vod_name, vod_actor, vod_score, vod_year
FROM sakura_movdetail
WHERE vod_actor LIKE '%{actor_name}%'
ORDER BY vod_time DESC
LIMIT 10
                    """.strip()
                    explanation = f"查询演员{actor_name}参演的作品"
                    return {"sql": sql, "explanation": explanation}
            
            if '导演' in question_lower or 'director' in question_lower:
                name_match = re.search(r'导演.*?([^\s，。？！,?!]+)', question)
                if name_match:
                    director_name = name_match.group(1)
                    sql = f"""
SELECT vod_id, vod_name, vod_director, vod_score, vod_year
FROM sakura_movdetail
WHERE vod_director LIKE '%{director_name}%'
ORDER BY vod_time DESC
LIMIT 10
                    """.strip()
                    explanation = f"查询导演{director_name}的作品"
                    return {"sql": sql, "explanation": explanation}
            
            # 年份查询
            year_match = re.search(r'(19|20)\d{2}', question)
            if year_match:
                year = year_match.group(0)
                sql = f"""
SELECT vod_id, vod_name, vod_year, vod_score, vod_area
FROM sakura_movdetail
WHERE vod_year LIKE '%{year}%'
ORDER BY vod_score DESC
LIMIT 10
                """.strip()
                explanation = f"查询{year}年的作品"
                return {"sql": sql, "explanation": explanation}
        
        # 规则2: 用户相关查询
        if '用户' in question_lower or 'user' in question_lower:
            if '数量' in question_lower or '多少' in question_lower or 'count' in question_lower:
                sql = "SELECT COUNT(*) as user_count FROM sakura_user"
                explanation = "查询用户总数"
                return {"sql": sql, "explanation": explanation}
            
            if '管理员' in question_lower or 'admin' in question_lower:
                sql = """
SELECT id, name, is_admin, created_at
FROM sakura_user
WHERE is_admin = 1
                """.strip()
                explanation = "查询所有管理员用户"
                return {"sql": sql, "explanation": explanation}
            
            if '最新' in question_lower or 'latest' in question_lower:
                num_match = re.search(r'(\d+)', question)
                limit = num_match.group(1) if num_match else '10'
                
                sql = f"""
SELECT id, name, created_at, is_admin
FROM sakura_user
ORDER BY created_at DESC
LIMIT {limit}
                """.strip()
                explanation = f"查询最新注册的{limit}个用户"
                return {"sql": sql, "explanation": explanation}
        
        # 规则3: 评论相关查询
        if '评论' in question_lower or 'comment' in question_lower:
            if '数量' in question_lower or '多少' in question_lower:
                sql = "SELECT COUNT(*) as comment_count FROM sakura_comment"
                explanation = "查询评论总数"
                return {"sql": sql, "explanation": explanation}
            
            if '最新' in question_lower or 'latest' in question_lower:
                num_match = re.search(r'(\d+)', question)
                limit = num_match.group(1) if num_match else '10'
                
                sql = f"""
SELECT c.id, c.body, c.timestamp, u.name as user_name
FROM sakura_comment c
LEFT JOIN sakura_user u ON c.user_id = u.id
ORDER BY c.timestamp DESC
LIMIT {limit}
                """.strip()
                explanation = f"查询最新的{limit}条评论"
                return {"sql": sql, "explanation": explanation}
        
        # 规则4: 统计查询
        if '统计' in question_lower or 'count' in question_lower or '总数' in question_lower:
            if '类型' in question_lower or 'type' in question_lower:
                sql = """
SELECT type_name, COUNT(*) as count
FROM sakura_movdetail
GROUP BY type_name
ORDER BY count DESC
                """.strip()
                explanation = "统计各类型电影的数量"
                return {"sql": sql, "explanation": explanation}
            
            if '地区' in question_lower or 'area' in question_lower:
                sql = """
SELECT vod_area, COUNT(*) as count
FROM sakura_movdetail
WHERE vod_area IS NOT NULL AND vod_area != ''
GROUP BY vod_area
ORDER BY count DESC
LIMIT 10
                """.strip()
                explanation = "统计各地区电影数量（前10）"
                return {"sql": sql, "explanation": explanation}
        
        # 默认：返回电影列表
        sql = """
SELECT vod_id, vod_name, vod_score, vod_year, type_name
FROM sakura_movdetail
ORDER BY vod_time DESC
LIMIT 10
        """.strip()
        explanation = "查询最新的10部电影（默认查询）"
        return {"sql": sql, "explanation": explanation}
    
    async def _generate_sql_with_llm(self, question: str) -> Dict[str, str]:
        """
        使用LLM生成SQL语句
        
        Args:
            question: 用户问题
            
        Returns:
            包含sql和explanation的字典
        """
        prompt = f"""你是一个专业的SQL生成助手。根据用户的自然语言问题，生成对应的MySQL查询语句。

数据库表结构：
{self.SCHEMA_INFO}

规则：
1. 只生成SELECT查询语句
2. 使用标准MySQL语法
3. 合理使用LIMIT限制结果数量
4. 对于模糊查询使用LIKE
5. 注意字段类型，评分需要CAST为DECIMAL
6. **重要：查询电影/视频数据时，必须在SELECT中包含 vod_id 字段（放在第一位）**

用户问题：{question}

请以JSON格式返回，包含以下字段：
{{
    "sql": "生成的SQL语句",
    "explanation": "简短的中文说明"
}}

只返回JSON，不要其他内容。
"""

        try:
            logger.info(f"Calling LLM API for question: {question}")
            async with httpx.AsyncClient(timeout=15.0) as client:  # 减少超时时间
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
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'].strip()
                    
                    # 尝试解析JSON
                    # 移除可能的markdown代码块标记
                    content = re.sub(r'```json\s*', '', content)
                    content = re.sub(r'```\s*$', '', content)
                    content = content.strip()
                    
                    result = json.loads(content)
                    logger.info(f"LLM generated SQL successfully")
                    return result
                else:
                    logger.error(f"LLM API error: {response.status_code} {response.text}")
                    raise Exception(f"LLM API failed with status {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error(f"LLM API timeout")
            raise Exception("LLM API timeout")
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            raise
    
    async def generate_and_execute_sql(
        self, 
        question: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        生成SQL并执行查询
        
        Args:
            question: 用户问题
            db: 数据库会话
            
        Returns:
            包含SQL、结果和说明的字典
        """
        try:
            # 优先使用LLM生成SQL，失败时降级到规则
            logger.info(f"Processing question: {question}")
            try:
                logger.info("Trying LLM generation...")
                sql_info = await self._generate_sql_with_llm(question)
                logger.info("LLM generation successful")
            except Exception as e:
                logger.warning(f"LLM generation failed: {str(e)}, fallback to rules")
                sql_info = self._generate_sql_with_rules(question)
                logger.info("Using rule-based generation")
            
            sql = sql_info["sql"]
            explanation = sql_info["explanation"]
            
            logger.info(f"Generated SQL: {sql}")
            
            # 安全检查：只允许SELECT语句
            if not sql.strip().upper().startswith('SELECT'):
                return {
                    "success": False,
                    "sql": sql,
                    "result": None,
                    "error": "出于安全考虑，只支持SELECT查询语句",
                    "explanation": explanation
                }
            
            # 执行SQL查询
            result = await db.execute(text(sql))
            rows = result.fetchall()
            
            # 转换结果为字典列表
            if rows:
                # 获取列名
                columns = result.keys()
                result_list = [dict(zip(columns, row)) for row in rows]
                
                # 处理特殊类型（如datetime）
                for item in result_list:
                    for key, value in item.items():
                        if hasattr(value, 'isoformat'):
                            item[key] = value.isoformat()
            else:
                result_list = []
            
            return {
                "success": True,
                "sql": sql,
                "result": result_list,
                "error": None,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            return {
                "success": False,
                "sql": sql if 'sql' in locals() else None,
                "result": None,
                "error": f"查询执行失败: {str(e)}",
                "explanation": explanation if 'explanation' in locals() else None
            }


# ==================== API 路由 ====================

@router.post("/ask", response_model=SQLResponse)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    智能搜索接口：接收自然语言问题，返回查询结果
    
    示例问题：
    - "查询评分最高的5部电影"
    - "最新的10部动漫"
    - "点击量最高的电影"
    - "2023年的电影有哪些"
    - "统计各类型电影数量"
    - "用户总数是多少"
    """
    logger.info(f"Received question: {request.question}")
    
    # 创建SQL Agent实例
    agent = SQLAgent()
    
    # 生成并执行SQL
    result = await agent.generate_and_execute_sql(request.question, db)
    
    return SQLResponse(**result)


@router.get("/schema")
async def get_database_schema():
    """
    获取数据库结构信息
    """
    return {
        "success": True,
        "schema": SQLAgent.SCHEMA_INFO,
        "message": "数据库结构信息"
    }


@router.get("/examples")
async def get_example_questions():
    """
    获取示例问题列表
    """
    examples = [
        {
            "category": "电影查询",
            "questions": [
                "查询评分最高的5部电影",
                "最新的10部电影",
                "点击量最高的10部电影",
                "查询动漫类型的作品",
                "2023年的电影有哪些"
            ]
        },
        {
            "category": "用户查询",
            "questions": [
                "用户总数是多少",
                "查询所有管理员",
                "最新注册的10个用户"
            ]
        },
        {
            "category": "评论查询",
            "questions": [
                "评论总数是多少",
                "最新的20条评论"
            ]
        },
        {
            "category": "统计查询",
            "questions": [
                "统计各类型电影数量",
                "统计各地区电影数量"
            ]
        }
    ]
    
    return {
        "success": True,
        "examples": examples,
        "message": "示例问题列表"
    }
