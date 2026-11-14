from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel

from ..models.models import UserCollection, MovDetail, User
from ..utils.auth_verify_util import get_current_user
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# 响应模型
class VodCollectionItem(BaseModel):
    vod_id: int
    vod_pic: str
    vod_name: str
    vod_remarks: str

class CollectionResponse(BaseModel):
    code: int
    message: str
    data: List[VodCollectionItem]

class IsCollectionResponse(BaseModel):
    code: int
    message: str
    data: int

class AddCollectionResponse(BaseModel):
    code: int
    message: str
    data: List[str]

@router.get("/show", response_model=dict)
async def show_collect_video(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    展示用户收藏的视频列表
    """
    # 验证用户权限
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "data": {
                    "code": 403,
                    "message": "无权限访问其他用户的收藏"
                }
            }
        )
    
    # 异步查询用户收藏
    result = await db.execute(
        select(UserCollection).filter(UserCollection.user_id == user_id)
    )
    user_collection = result.scalar_one_or_none()
    
    collect_vod_list = []
    if user_collection and user_collection.movdetail_id_list:
        # 解析收藏的视频ID列表
        store_vod_list = user_collection.movdetail_id_list.split(';')[:-1]
        
        # 异步分页查询视频详情
        page_size = 12
        offset = (page - 1) * page_size
        query = select(MovDetail).filter(
            MovDetail.id.in_(store_vod_list)
        ).order_by(desc(MovDetail.vod_time)).offset(offset).limit(page_size)
        
        result = await db.execute(query)
        collect_movs = result.scalars().all()
        
        # 构建响应数据
        for mov in collect_movs:
            collect_vod_list.append({
                "vod_id": mov.vod_id,  # 使用真正的 vod_id，不是数据库主键 id
                "vod_pic": mov.vod_pic or "",
                "vod_name": mov.vod_name or "",
                "vod_remarks": mov.vod_remarks or ""
            })
    
    return {
        "data": {
            "code": 200,
            "message": "收藏的视频信息",
            "data": collect_vod_list
        }
    }

@router.get("/is_collection", response_model=dict)
async def show_is_collect_video(
    user_id: int = Query(..., description="用户ID"),
    vod_id: str = Query(..., description="视频ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查视频是否已被收藏
    """
    # 验证用户权限
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "data": {
                    "code": 403,
                    "message": "无权限访问其他用户的收藏"
                }
            }
        )
    
    # 异步查询用户收藏
    result = await db.execute(
        select(UserCollection).filter(UserCollection.user_id == user_id)
    )
    user_collection = result.scalar_one_or_none()
    
    # 检查是否已收藏
    if user_collection and user_collection.movdetail_id_list:
        if vod_id in user_collection.movdetail_id_list:
            return {
                "data": {
                    "code": 200,
                    "message": "该视频已被收藏",
                    "data": 1
                }
            }
    
    return {
        "data": {
            "code": 200,
            "message": "该视频未被收藏",
            "data": 0
        }
    }

@router.get("/add", response_model=dict)
async def add_collect_video(
    user_id: int = Query(..., description="用户ID"),
    vod_id: str = Query(..., description="视频ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    添加视频到收藏
    """
    # 验证用户权限
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "data": {
                    "code": 403,
                    "message": "无权限修改其他用户的收藏"
                }
            }
        )
    
    # 异步验证视频是否存在
    result = await db.execute(select(MovDetail).filter(MovDetail.id == int(vod_id)))
    mov_detail = result.scalar_one_or_none()
    if not mov_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "data": {
                    "code": 404,
                    "message": "视频不存在"
                }
            }
        )
    
    try:
        # 异步查询或创建用户收藏记录
        result = await db.execute(
            select(UserCollection).filter(UserCollection.user_id == user_id)
        )
        user_collection = result.scalar_one_or_none()
        
        store_vod_list = [vod_id]
        
        if user_collection:
            # 更新现有收藏
            if user_collection.movdetail_id_list:
                store_vod_list.extend(user_collection.movdetail_id_list.split(';'))
            
            if vod_id + ';' not in user_collection.movdetail_id_list:
                user_collection.add_vod_id(vod_id)
        else:
            # 创建新的收藏记录
            user_collection = UserCollection(
                user_id=user_id,
                movdetail_id_list=vod_id + ';'
            )
            db.add(user_collection)
        
        await db.commit()
        
        # 去重并返回收藏列表
        unique_vod_list = list(set(store_vod_list))
        
        return {
            "data": {
                "code": 200,
                "message": "视频收藏成功",
                "data": unique_vod_list
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "data": {
                    "code": 500,
                    "message": "视频收藏失败"
                }
            }
        )