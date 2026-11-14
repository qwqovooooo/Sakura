"""
管理后台 - 用户管理模块
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func
from pydantic import BaseModel
from datetime import datetime

from ..models.models import User, Comment, UserCollection
from ..utils.auth_verify_util import get_current_user
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# ==================== 数据模型 ====================
class UserListItem(BaseModel):
    id: int
    name: str
    is_admin: bool
    created_at: str
    comment_count: int
    collection_count: int

class UserUpdateRequest(BaseModel):
    is_admin: Optional[bool] = None

# ==================== 权限验证 ====================
async def verify_admin(current_user: User = Depends(get_current_user)):
    """验证管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"data": {"code": 403, "message": "需要管理员权限"}}
        )
    return current_user

# ==================== 用户管理接口 ====================
@router.get("/users", response_model=dict)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    """
    # 构建查询
    query = select(User)
    
    # 关键词搜索
    if keyword:
        query = query.where(User.name.like(f"%{keyword}%"))
    
    # 排序和分页
    query = query.order_by(desc(User.created_at))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(query)
    users = result.scalars().all()
    
    # 统计总数
    count_query = select(func.count(User.id))
    if keyword:
        count_query = count_query.where(User.name.like(f"%{keyword}%"))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 统计管理员总数（所有管理员，不只是当前页）
    admin_count_query = select(func.count(User.id)).where(User.is_admin == True)
    if keyword:
        admin_count_query = admin_count_query.where(User.name.like(f"%{keyword}%"))
    admin_count_result = await db.execute(admin_count_query)
    admin_count = admin_count_result.scalar() or 0
    
    # 构建响应数据
    user_list = []
    for user in users:
        # 统计评论数
        comment_count_query = select(func.count(Comment.id)).where(Comment.user_id == user.id)
        comment_count_result = await db.execute(comment_count_query)
        comment_count = comment_count_result.scalar() or 0
        
        # 统计收藏数
        collection_query = select(UserCollection).where(UserCollection.user_id == user.id)
        collection_result = await db.execute(collection_query)
        collection = collection_result.scalar_one_or_none()
        collection_count = len(collection.movdetail_id_list.split(';')) - 1 if collection and collection.movdetail_id_list else 0
        
        user_list.append({
            "id": user.id,
            "name": user.name,
            "is_admin": user.is_admin,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            "comments_count": comment_count,
            "collections_count": collection_count
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "users": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "admin_count": admin_count  # 使用真实的管理员总数
        }
    }

@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息（仅管理员）
    """
    # 查询用户
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "用户不存在"}}
        )
    
    # 更新数据
    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin
    
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

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户（仅管理员）
    """
    # 不能删除自己
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"data": {"code": 400, "message": "不能删除自己"}}
        )
    
    # 查询用户
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "用户不存在"}}
        )
    
    try:
        await db.delete(user)
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
