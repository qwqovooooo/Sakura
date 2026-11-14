"""
管理后台 - 评论管理模块
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func, or_
from pydantic import BaseModel
from datetime import datetime

from ..models.models import Comment, User, MovDetail
from ..utils.auth_verify_util import get_current_user
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# ==================== 数据模型 ====================
class CommentUpdateRequest(BaseModel):
    body: Optional[str] = None
    reviewed: Optional[bool] = None

# ==================== 权限验证 ====================
async def verify_admin(current_user: User = Depends(get_current_user)):
    """验证管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"data": {"code": 403, "message": "需要管理员权限"}}
        )
    return current_user

# ==================== 评论管理接口 ====================
@router.get("/comments", response_model=dict)
async def get_comments_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    reviewed: Optional[bool] = Query(None, description="审核状态"),
    movie_id: Optional[int] = Query(None, description="电影ID"),
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取评论列表（仅管理员）
    """
    # 构建查询
    query = select(Comment)
    
    # 关键词搜索
    if keyword:
        query = query.where(Comment.body.like(f"%{keyword}%"))
    
    # 审核状态筛选
    if reviewed is not None:
        query = query.where(Comment.reviewed == reviewed)
    
    # 电影筛选
    if movie_id:
        query = query.where(Comment.movdetail_id == movie_id)
    
    # 排序和分页
    query = query.order_by(desc(Comment.timestamp))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # 统计总数
    count_query = select(func.count(Comment.id))
    if keyword:
        count_query = count_query.where(Comment.body.like(f"%{keyword}%"))
    if reviewed is not None:
        count_query = count_query.where(Comment.reviewed == reviewed)
    if movie_id:
        count_query = count_query.where(Comment.movdetail_id == movie_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 构建响应数据
    comment_list = []
    for comment in comments:
        # 获取用户信息
        user_result = await db.execute(select(User).filter(User.id == comment.user_id))
        user = user_result.scalar_one_or_none()
        
        # 获取电影信息
        movie_info = None
        if comment.movdetail_id:
            movie_result = await db.execute(select(MovDetail).filter(MovDetail.id == comment.movdetail_id))
            movie = movie_result.scalar_one_or_none()
            if movie:
                movie_info = {
                    "id": movie.id,
                    "name": movie.vod_name
                }
        
        # 获取回复对象
        reply_to = None
        if comment.replied_id:
            replied_result = await db.execute(select(Comment).filter(Comment.id == comment.replied_id))
            replied_comment = replied_result.scalar_one_or_none()
            if replied_comment:
                replied_user_result = await db.execute(select(User).filter(User.id == replied_comment.user_id))
                replied_user = replied_user_result.scalar_one_or_none()
                reply_to = {
                    "id": replied_comment.id,
                    "user_name": replied_user.name if replied_user else "未知用户"
                }
        
        comment_list.append({
            "id": comment.id,
            "content": comment.body,  # 前端期望 content 不是 body
            "reviewed": comment.reviewed,
            "created_at": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S") if comment.timestamp else "",  # 前端期望 created_at 不是 timestamp
            "user_id": comment.user_id,
            "user_name": user.name if user else "未知用户",
            "movie_name": movie_info["name"] if movie_info else "",  # 前端期望 movie_name 不是 movie 对象
            "movie_id": movie_info["id"] if movie_info else None,
            "reply_to": reply_to
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "comments": comment_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }

@router.put("/comments/{comment_id}", response_model=dict)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdateRequest,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新评论（仅管理员）
    """
    # 查询评论
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "评论不存在"}}
        )
    
    # 更新数据
    if update_data.body is not None:
        comment.body = update_data.body
    if update_data.reviewed is not None:
        comment.reviewed = update_data.reviewed
    
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

@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除评论（仅管理员）
    """
    # 查询评论
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"data": {"code": 404, "message": "评论不存在"}}
        )
    
    try:
        await db.delete(comment)
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

@router.post("/comments/batch-delete", response_model=dict)
async def batch_delete_comments(
    comment_ids: List[int],
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    批量删除评论（仅管理员）
    """
    try:
        deleted_count = 0
        for comment_id in comment_ids:
            result = await db.execute(select(Comment).filter(Comment.id == comment_id))
            comment = result.scalar_one_or_none()
            if comment:
                await db.delete(comment)
                deleted_count += 1
        
        await db.commit()
        return {
            "code": 200,
            "message": f"成功删除 {deleted_count} 条评论",
            "data": {"deleted_count": deleted_count}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"data": {"code": 500, "message": f"批量删除失败: {str(e)}"}}
        )
