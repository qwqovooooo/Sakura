"""
管理后台 - 电影管理模块
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func, or_
from pydantic import BaseModel
from datetime import datetime

from ..models.models import MovDetail, User
from ..utils.auth_verify_util import get_current_user
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# ==================== 数据模型 ====================
class MovieCreateRequest(BaseModel):
    vod_name: str
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    vod_en: Optional[str] = None
    vod_pic: Optional[str] = None
    vod_actor: Optional[str] = None
    vod_director: Optional[str] = None
    vod_content: Optional[str] = None
    vod_area: Optional[str] = None
    vod_year: Optional[str] = None
    vod_remarks: Optional[str] = None
    vod_play_url: Optional[str] = None  # 播放地址

class MovieUpdateRequest(BaseModel):
    vod_name: Optional[str] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    vod_pic: Optional[str] = None
    vod_actor: Optional[str] = None
    vod_director: Optional[str] = None
    vod_content: Optional[str] = None
    vod_area: Optional[str] = None
    vod_year: Optional[str] = None
    vod_remarks: Optional[str] = None
    vod_play_url: Optional[str] = None  # 播放地址

# ==================== 权限验证 ====================
async def verify_admin(current_user: User = Depends(get_current_user)):
    """验证管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"data": {"code": 403, "message": "需要管理员权限"}}
        )
    return current_user

# ==================== 电影管理接口 ====================
@router.get("/movies", response_model=dict)
async def get_movies_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    type_id: Optional[int] = Query(None, description="类型ID"),
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取电影列表（仅管理员）
    """
    # 构建查询
    query = select(MovDetail)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                MovDetail.vod_name.like(f"%{keyword}%"),
                MovDetail.vod_actor.like(f"%{keyword}%"),
                MovDetail.vod_director.like(f"%{keyword}%")
            )
        )
    
    # 类型筛选
    if type_id:
        query = query.where(MovDetail.type_id == type_id)
    
    # 排序和分页
    query = query.order_by(desc(MovDetail.vod_time))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(query)
    movies = result.scalars().all()
    
    # 统计总数
    count_query = select(func.count(MovDetail.id))
    if keyword:
        count_query = count_query.where(
            or_(
                MovDetail.vod_name.like(f"%{keyword}%"),
                MovDetail.vod_actor.like(f"%{keyword}%"),
                MovDetail.vod_director.like(f"%{keyword}%")
            )
        )
    if type_id:
        count_query = count_query.where(MovDetail.type_id == type_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 构建响应数据
    movie_list = []
    for movie in movies:
        movie_list.append({
            "id": movie.id,
            "vod_id": movie.vod_id,
            "vod_name": movie.vod_name,
            "type_id": movie.type_id,
            "type_name": movie.type_name,
            "vod_pic": movie.vod_pic,
            "vod_actor": movie.vod_actor,
            "vod_director": movie.vod_director,
            "vod_area": movie.vod_area,
            "vod_year": movie.vod_year,
            "vod_remarks": movie.vod_remarks,
            "vod_time": movie.vod_time.strftime("%Y-%m-%d %H:%M:%S") if movie.vod_time else ""
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "movies": movie_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }

@router.post("/movies", response_model=dict)
async def create_movie(
    movie_data: MovieCreateRequest,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建电影（仅管理员）
    """
    try:
        # 生成 vod_id
        max_vod_id_query = select(func.max(MovDetail.vod_id))
        max_vod_id_result = await db.execute(max_vod_id_query)
        max_vod_id = max_vod_id_result.scalar() or 0
        new_vod_id = max_vod_id + 1
        
        # 根据 type_name 自动设置 type_id（如果没有提供）
        type_id = movie_data.type_id
        if not type_id and movie_data.type_name:
            # 类型名称到 type_id 的映射
            type_name_to_id = {
                "国产剧": 13,
                "电影": 1,
                "电视剧": 2,
                "综艺": 3,
                "动漫": 4,
                "美剧": 14,
                "韩剧": 15,
                "英剧": 16,
                "港剧": 23,
                "日剧": 24,
                "泰剧": 25
            }
            type_id = type_name_to_id.get(movie_data.type_name, 1)  # 默认为电影
        
        # 创建电影
        new_movie = MovDetail(
            vod_id=new_vod_id,
            vod_name=movie_data.vod_name,
            type_id=type_id,
            type_name=movie_data.type_name,
            vod_en=movie_data.vod_en,
            vod_pic=movie_data.vod_pic,
            vod_actor=movie_data.vod_actor,
            vod_director=movie_data.vod_director,
            vod_content=movie_data.vod_content,
            vod_area=movie_data.vod_area,
            vod_year=movie_data.vod_year,
            vod_remarks=movie_data.vod_remarks,
            vod_play_url=movie_data.vod_play_url,  # 保存播放地址
            vod_time=datetime.now()
        )
        
        db.add(new_movie)
        await db.commit()
        await db.refresh(new_movie)
        
        return {
            "code": 200,
            "message": "创建成功",
            "data": {"id": new_movie.id}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"data": {"code": 500, "message": f"创建失败: {str(e)}"}}
        )

@router.put("/movies/{vod_id}", response_model=dict)
async def update_movie(
    vod_id: int,
    update_data: MovieUpdateRequest,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新电影信息（仅管理员）
    """
    # 查询电影（使用 vod_id 而不是 id）
    result = await db.execute(select(MovDetail).filter(MovDetail.vod_id == vod_id))
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "电影不存在"}}
        )
    
    # 更新数据
    if update_data.vod_name is not None:
        movie.vod_name = update_data.vod_name
    if update_data.type_id is not None:
        movie.type_id = update_data.type_id
    if update_data.type_name is not None:
        movie.type_name = update_data.type_name
        # 如果没有 type_id，根据 type_name 自动设置
        if not movie.type_id:
            type_name_to_id = {
                "国产剧": 13, "电影": 1, "电视剧": 2, "综艺": 3, "动漫": 4,
                "美剧": 14, "韩剧": 15, "英剧": 16, "港剧": 23, "日剧": 24, "泰剧": 25
            }
            movie.type_id = type_name_to_id.get(update_data.type_name, 1)
    if update_data.vod_pic is not None:
        movie.vod_pic = update_data.vod_pic
    if update_data.vod_actor is not None:
        movie.vod_actor = update_data.vod_actor
    if update_data.vod_director is not None:
        movie.vod_director = update_data.vod_director
    if update_data.vod_content is not None:
        movie.vod_content = update_data.vod_content
    if update_data.vod_area is not None:
        movie.vod_area = update_data.vod_area
    if update_data.vod_year is not None:
        movie.vod_year = update_data.vod_year
    if update_data.vod_remarks is not None:
        movie.vod_remarks = update_data.vod_remarks
    if update_data.vod_play_url is not None:
        movie.vod_play_url = update_data.vod_play_url  # 更新播放地址
    
    try:
        await db.commit()
        return {
            "code": 200,
            "message": "更新成功"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"data": {"code": 500, "message": f"更新失败: {str(e)}"}}
        )

@router.delete("/movies/{vod_id}", response_model=dict)
async def delete_movie(
    vod_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除电影（仅管理员）
    """
    # 查询电影（使用 vod_id 而不是 id）
    result = await db.execute(select(MovDetail).filter(MovDetail.vod_id == vod_id))
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "电影不存在"}}
        )
    
    try:
        await db.delete(movie)
        await db.commit()
        return {
            "code": 200,
            "message": "删除成功"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"data": {"code": 500, "message": f"删除失败: {str(e)}"}}
        )

@router.get("/movies/{vod_id}", response_model=dict)
async def get_movie_detail(
    vod_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取电影详情（仅管理员）
    """
    result = await db.execute(select(MovDetail).filter(MovDetail.vod_id == vod_id))
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "电影不存在"}}
        )
    
    return {
        "data": {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": movie.id,
                "vod_id": movie.vod_id,
                "vod_name": movie.vod_name,
                "type_id": movie.type_id,
                "type_name": movie.type_name,
                "vod_en": movie.vod_en,
                "vod_pic": movie.vod_pic,
                "vod_actor": movie.vod_actor,
                "vod_director": movie.vod_director,
                "vod_content": movie.vod_content,
                "vod_area": movie.vod_area,
                "vod_year": movie.vod_year,
                "vod_remarks": movie.vod_remarks,
                "vod_play_url": movie.vod_play_url,
                "vod_time": movie.vod_time.strftime("%Y-%m-%d %H:%M:%S") if movie.vod_time else ""
            }
        }
    }
