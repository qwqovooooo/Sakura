from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel

from ..models.models import Comment, User, MovDetail
from ..utils.auth_verify_util import get_current_user
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# 请求模型
class CommentRequest(BaseModel):
    body: str
    user_id: int

# 评论响应模型
class ReplyItem(BaseModel):
    user_name: str
    id: int
    reply_user_name: str
    body: str
    time: str

class CommentItem(BaseModel):
    user_name: str
    body: str
    time: str
    id: int
    reply_list: List[ReplyItem]

class CommentListResponse(BaseModel):
    code: int
    data: List[CommentItem]
    message: str

class MessageResponse(BaseModel):
    code: int
    message: str

def get_all_replies(reply_comments: List[Comment]) -> List[Dict[str, Any]]:
    """
    递归获取所有回复
    """
    result = []
    for comment in reply_comments:
        reply = {
            "user_name": comment.user.name,
            "id": comment.id,
            "reply_user_name": comment.replied.user.name if comment.replied else "",
            "body": comment.body,
            "time": comment.timestamp.strftime('%Y-%m-%d')
        }
        result.append(reply)
        if comment.replies:
            result.extend(get_all_replies(comment.replies))
    return result

@router.get("/show/comment/{vod_id}", response_model=dict)
async def show_comments(
    vod_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    展示指定视频的评论
    """
    # 异步查询评论
    result = await db.execute(
        select(Comment)
        .filter(Comment.movdetail_id == vod_id)
        .order_by(desc(Comment.timestamp))
    )
    comments = result.scalars().all()
    
    comment_list = []
    for comment in comments:
        # 只处理顶级评论（没有被回复的评论）
        if not comment.replied_id:
            c = {
                "user_name": comment.user.name,
                "body": comment.body,
                "time": comment.timestamp.strftime('%Y-%m-%d'),
                "id": comment.id,
                "reply_list": get_all_replies(comment.replies)
            }
            comment_list.append(c)
    
    return {
        "data": {
            "code": 200,
            "data": comment_list,
            "message": "评论获取成功"
        }
    }

@router.post("/publish/comment/{vod_id}", response_model=dict)
async def post_comments(
    vod_id: int,
    comment_data: CommentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发表评论（无需登录）
    """
    # 异步验证视频是否存在
    result = await db.execute(select(MovDetail).filter(MovDetail.id == vod_id))
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
        # 创建评论
        comment = Comment(
            body=comment_data.body,
            user_id=comment_data.user_id,
            movdetail_id=vod_id
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        
        return {
            "data": {
                "code": 200,
                "message": "评论发布成功"
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "data": {
                    "code": 500,
                    "message": "评论发布失败"
                }
            }
        )

@router.post("/reply/comment/{comment_id}", response_model=dict)
async def reply_comment(
    comment_id: int,
    comment_data: CommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    回复评论
    """
    # 验证用户权限
    if current_user.id != comment_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "data": {
                    "code": 403,
                    "message": "无权限操作"
                }
            }
        )
    
    # 异步验证被回复的评论是否存在
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    parent_comment = result.scalar_one_or_none()
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "data": {
                    "code": 404,
                    "message": "被回复的评论不存在"
                }
            }
        )
    
    try:
        # 创建回复评论
        r_comment = Comment(
            body=comment_data.body,
            user_id=comment_data.user_id,
            replied_id=comment_id
        )
        db.add(r_comment)
        await db.commit()
        await db.refresh(r_comment)
        
        return {
            "data": {
                "code": 200,
                "message": "评论回复成功"
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "data": {
                    "code": 500,
                    "message": "评论回复失败"
                }
            }
        )