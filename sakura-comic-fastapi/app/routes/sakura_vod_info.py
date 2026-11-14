import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc
from pydantic import BaseModel
from pathlib import Path
import aiofiles

from ..models.models import MovDetail, MovInfo, MovType
from ..config import AsyncSessionLocal

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()

# 视频类型映射字典
mov_type_dict = {
    1: [1, 6, 7, 8, 9, 10, 11, 39],  # 电影（包括动画电影）
    2: [2, 13, 14, 15, 16, 17, 18, 19, 23],  # 连续剧
    3: [3, 25, 26, 27],  # 综艺
    4: [4, 29, 30, 31],  # 动漫
    5: [5],  # 资讯
    0: [1, 2, 3, 4, 5]  # 全部
}

# 响应模型
class VodListItem(BaseModel):
    vod_id: int
    vod_pic: Optional[str]
    vod_name: Optional[str]
    vod_remarks: Optional[str]

class VodListResponse(BaseModel):
    code: int
    message: str
    data: List[VodListItem]

class VodDetailResponse(BaseModel):
    code: int
    data: Optional[Dict[str, Any]]
    msg: str

@router.get("/vod_list", response_model=dict)
async def get_vod_list(
    page: int = Query(1, ge=1, description="页码"),
    movtype: int = Query(0, description="视频类型，一级类型"),
    vod_area: Optional[str] = Query(None, description="视频地区"),
    vod_class: Optional[str] = Query(None, description="视频二级类型"),
    vod_year: Optional[str] = Query(None, description="视频年份"),
    keyword: Optional[str] = Query(None, description="关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取视频列表
    """
    # 获取视频类型列表
    mov_type_list = mov_type_dict.get(movtype, [])
    
    # 构建异步查询
    query = select(MovDetail)
    
    # 应用过滤条件
    if vod_class:
        query = query.filter(MovDetail.type_name == vod_class)
    else:
        query = query.filter(MovDetail.type_id.in_(mov_type_list))
    
    # 地区过滤
    if vod_area:
        if vod_area != 'more':
            query = query.filter(MovDetail.vod_area == vod_area)
        else:
            query = query.where(
                ~MovDetail.vod_area.in_(["中国", "内地", "美国", "日本", "韩国", "英国", "法国", "香港", "泰国"])
            )
    
    # 年份过滤
    if vod_year:
        if vod_year != 'more':
            query = query.filter(MovDetail.vod_year == vod_year)
        else:
            query = query.where(
                ~MovDetail.vod_year.in_([
                    "2023", "2022", "2021", "2020", "2019", "2018", "2017",
                    "2016", "2015", "2014", "2013", "2012", "2011", "2010"
                ])
            )
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                MovDetail.vod_name.like(f"%{keyword}%"),
                MovDetail.vod_content.like(f"%{keyword}%"),
                MovDetail.vod_director.like(f"%{keyword}%"),
                MovDetail.vod_actor.like(f"%{keyword}%")
            )
        )
    
    # 排序和分页
    query = query.order_by(desc(MovDetail.vod_time))
    
    # 分页（每页8条，减少加载量）
    page_size = 8
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行异步查询
    result = await db.execute(query)
    movies = result.scalars().all()
    
    # 构建响应数据
    vod_list = []
    for mov in movies:
        vod_list.append({
            "vod_id": mov.vod_id,  # 使用真正的 vod_id，不是数据库主键 id
            "vod_pic": mov.vod_pic,
            "vod_name": mov.vod_name,
            "vod_remarks": mov.vod_remarks
        })
    
    return {
        "code": 200,
        "message": "success",
        "data": vod_list
    }

@router.get("/vod_detail", response_model=dict)
async def get_vod_detail(
    vod_id: int = Query(..., description="视频ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取视频详情
    """
    # 异步查询视频详情（使用 vod_id 而不是数据库主键 id）
    result = await db.execute(select(MovDetail).filter(MovDetail.vod_id == vod_id))
    mov = result.scalar_one_or_none()
    
    if not mov:
        return {
            "code": 400,
            "msg": "failed no this mov"
        }
    
    # 处理内容
    if mov.vod_content:
        mov.vod_content = mov.vod_content.replace('<p>', '') \
            .replace('</p>', '').replace('<span>', '').replace('</span>', '')
    
    # 处理播放地址
    pay_url_dict = {}
    if mov.vod_play_url:
        for play_url_set in mov.vod_play_url.split('#'):
            try:
                k, v = play_url_set.split('$')
                pay_url_dict[k] = v
            except ValueError:
                continue
        mov.vod_play_url = pay_url_dict
    
    # 格式化时间
    if mov.vod_time:
        mov.vod_time = mov.vod_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建响应数据
    result = {
        "id": mov.id,
        "type_id": mov.type_id,
        "type_name": mov.type_name,
        "vod_name": mov.vod_name,
        "vod_en": mov.vod_en,
        "vod_actor": mov.vod_actor,
        "vod_director": mov.vod_director,
        "vod_area": mov.vod_area,
        "vod_year": mov.vod_year,
        "vod_content": mov.vod_content,
        "vod_play_url": mov.vod_play_url,
        "vod_play_from": mov.vod_play_from,
        "vod_pic": mov.vod_pic,
        "vod_remarks": mov.vod_remarks,
        "vod_time": mov.vod_time,
        "vod_state": mov.vod_state,
        "vod_score": mov.vod_score,
        "vod_hits": mov.vod_hits
    }
    
    # 添加其他可能的字段
    for attr in vars(mov):
        if attr not in result and not attr.startswith('_'):
            result[attr] = getattr(mov, attr)
    
    return {
        "code": 200,
        "data": result,
        "msg": "success"
    }

@router.get("/imgs/{img}")
async def get_img_info(img: str):
    """
    异步获取图片信息
    """
    # 获取图片路径
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    filepath = os.path.join(basedir, f"static/imgs/{img}")
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 异步读取文件内容
    try:
        async with aiofiles.open(filepath, "rb") as f:
            content = await f.read()
        
        # 确定MIME类型
        if img.endswith('.jpg') or img.endswith('.jpeg'):
            media_type = "image/jpeg"
        elif img.endswith('.png'):
            media_type = "image/png"
        elif img.endswith('.gif'):
            media_type = "image/gif"
        else:
            media_type = "application/octet-stream"
        
        return Response(content=content, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))