"""
直播功能模块 - 支持OBS Studio推流
"""
import logging
import hashlib
import secrets
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from ..config import AsyncSessionLocal, Base
from ..models.models import User
from ..utils.auth_verify_util import get_current_user

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


# ==================== 数据库模型 ====================

class LiveRoom(Base):
    """直播间表"""
    __tablename__ = "live_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(50), unique=True, index=True, nullable=False, comment="直播间ID")
    title = Column(String(200), nullable=False, comment="直播间标题")
    description = Column(Text, comment="直播间描述")
    
    # 主播信息
    user_id = Column(Integer, nullable=False, index=True, comment="主播用户ID")
    anchor_name = Column(String(50), comment="主播名称")
    
    # 直播状态
    status = Column(String(20), default="offline", comment="直播状态: online/offline/banned")
    is_live = Column(Boolean, default=False, comment="是否正在直播")
    
    # 推流信息
    stream_key = Column(String(100), unique=True, nullable=False, comment="推流密钥")
    rtmp_url = Column(String(200), comment="RTMP推流地址")
    
    # 播放地址
    hls_url = Column(String(200), comment="HLS播放地址")
    flv_url = Column(String(200), comment="FLV播放地址")
    
    # 统计信息
    viewer_count = Column(Integer, default=0, comment="当前观看人数")
    total_viewers = Column(Integer, default=0, comment="累计观看人数")
    like_count = Column(Integer, default=0, comment="点赞数")
    
    # 封面和分类
    cover_image = Column(String(500), comment="直播间封面")
    category = Column(String(50), comment="直播分类")
    
    # 外部直播源支持
    source_type = Column(String(20), default="self", comment="直播源类型: self/external")
    source_url = Column(String(500), nullable=True, comment="外部直播源地址")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    started_at = Column(DateTime, comment="开播时间")
    ended_at = Column(DateTime, comment="下播时间")
    
    def __repr__(self):
        return f"<LiveRoom {self.room_id}: {self.title}>"


# ==================== 请求/响应模型 ====================

class CreateLiveRoomRequest(BaseModel):
    """创建直播间请求"""
    title: str = Field(..., min_length=1, max_length=200, description="直播间标题")
    description: Optional[str] = Field(None, description="直播间描述")
    category: Optional[str] = Field("娱乐", description="直播分类")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    source_url: Optional[str] = Field(None, description="外部直播源地址（HLS/FLV）")
    source_type: Optional[str] = Field("self", description="直播源类型: self/external")


class LiveRoomResponse(BaseModel):
    """直播间响应"""
    id: int
    room_id: str
    title: str
    description: Optional[str]
    anchor_name: str
    status: str
    is_live: bool
    viewer_count: int
    total_viewers: int
    like_count: int
    cover_image: Optional[str]
    category: Optional[str]
    source_type: Optional[str] = "self"
    source_url: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime]
    
    # 推流信息（仅主播可见）
    stream_key: Optional[str] = None
    rtmp_url: Optional[str] = None
    
    # 播放地址
    hls_url: Optional[str] = None
    flv_url: Optional[str] = None


class StreamUrlResponse(BaseModel):
    """推流地址响应"""
    rtmp_url: str
    stream_key: str
    push_url: str  # 完整推流地址
    hls_url: str
    flv_url: str


# ==================== 数据库依赖 ====================

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# ==================== 辅助函数 ====================

def generate_room_id() -> str:
    """生成唯一的直播间ID"""
    timestamp = int(datetime.now().timestamp() * 1000)
    random_str = secrets.token_hex(4)
    return f"room_{timestamp}_{random_str}"


def generate_stream_key() -> str:
    """生成推流密钥"""
    return secrets.token_urlsafe(32)


def build_stream_urls(room_id: str, stream_key: str) -> dict:
    """
    构建推流和播放地址
    
    使用七牛云直播服务
    请在七牛云控制台获取以下地址并填入：
    1. RTMP 推流域名
    2. HLS/FLV 播放域名
    """
    # ========== 配置区域 ==========
    # TODO: 请在七牛云控制台获取以下地址
    
    # 推流域名（RTMP）
    RTMP_PUSH_DOMAIN = "rtmp://pili-publish.your-domain.com"  # 替换为你的推流域名
    
    # 播放域名（HLS/FLV）
    HLS_PLAY_DOMAIN = "http://pili-live-hls.your-domain.com"  # 替换为你的HLS播放域名
    FLV_PLAY_DOMAIN = "http://pili-live-hdl.your-domain.com"  # 替换为你的FLV播放域名
    
    # 直播流名（使用 room_id 作为流名）
    stream_name = room_id
    
    # ========== 地址生成 ==========
    return {
        "rtmp_url": f"{RTMP_PUSH_DOMAIN}/live",
        "stream_key": f"{stream_name}?key={stream_key}",
        "hls_url": f"{HLS_PLAY_DOMAIN}/live/{stream_name}.m3u8",
        "flv_url": f"{FLV_PLAY_DOMAIN}/live/{stream_name}.flv"
    }


# ==================== API 路由 ====================

@router.post("/create", response_model=LiveRoomResponse)
async def create_live_room(
    request: CreateLiveRoomRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建直播间
    
    - 用户需要登录
    - 每个用户只能创建一个直播间
    """
    logger.info(f"用户 {current_user.name} 请求创建直播间")
    
    try:
        # 检查用户是否已有直播间
        result = await db.execute(
            select(LiveRoom).where(LiveRoom.user_id == current_user.id)
        )
        existing_room = result.scalar_one_or_none()
        
        if existing_room:
            # 如果已有直播间，返回现有直播间信息
            logger.info(f"用户已有直播间: {existing_room.room_id}")
            return LiveRoomResponse(
                id=existing_room.id,
                room_id=existing_room.room_id,
                title=existing_room.title,
                description=existing_room.description,
                anchor_name=existing_room.anchor_name,
                status=existing_room.status,
                is_live=existing_room.is_live,
                viewer_count=existing_room.viewer_count,
                total_viewers=existing_room.total_viewers,
                like_count=existing_room.like_count,
                cover_image=existing_room.cover_image,
                category=existing_room.category,
                source_type=existing_room.source_type,
                source_url=existing_room.source_url,
                created_at=existing_room.created_at,
                started_at=existing_room.started_at,
                stream_key=existing_room.stream_key,
                rtmp_url=existing_room.rtmp_url,
                hls_url=existing_room.hls_url,
                flv_url=existing_room.flv_url
            )
        
        # 生成直播间ID和推流密钥
        room_id = generate_room_id()
        stream_key = generate_stream_key()
        
        # 构建推流和播放地址
        stream_urls = build_stream_urls(room_id, stream_key)
        
        # 创建直播间
        new_room = LiveRoom(
            room_id=room_id,
            title=request.title,
            description=request.description,
            user_id=current_user.id,
            anchor_name=current_user.name,
            stream_key=stream_key,
            rtmp_url=stream_urls["rtmp_url"],
            hls_url=stream_urls["hls_url"],
            flv_url=stream_urls["flv_url"],
            cover_image=request.cover_image,
            category=request.category,
            source_type=request.source_type,
            source_url=request.source_url,
            status="offline",
            is_live=False
        )
        
        db.add(new_room)
        await db.commit()
        await db.refresh(new_room)
        
        logger.info(f"直播间创建成功: {room_id}")
        
        return LiveRoomResponse(
            id=new_room.id,
            room_id=new_room.room_id,
            title=new_room.title,
            description=new_room.description,
            anchor_name=new_room.anchor_name,
            status=new_room.status,
            is_live=new_room.is_live,
            viewer_count=new_room.viewer_count,
            total_viewers=new_room.total_viewers,
            like_count=new_room.like_count,
            cover_image=new_room.cover_image,
            category=new_room.category,
            created_at=new_room.created_at,
            started_at=new_room.started_at,
            stream_key=new_room.stream_key,
            rtmp_url=new_room.rtmp_url,
            hls_url=new_room.hls_url,
            flv_url=new_room.flv_url
        )
        
    except Exception as e:
        logger.error(f"创建直播间失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建直播间失败: {str(e)}"
        )


@router.get("/my-room", response_model=LiveRoomResponse)
async def get_my_live_room(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的直播间信息"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.user_id == current_user.id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在，请先创建直播间"
        )
    
    return LiveRoomResponse(
        id=room.id,
        room_id=room.room_id,
        title=room.title,
        description=room.description,
        anchor_name=room.anchor_name,
        status=room.status,
        is_live=room.is_live,
        viewer_count=room.viewer_count,
        total_viewers=room.total_viewers,
        like_count=room.like_count,
        cover_image=room.cover_image,
        category=room.category,
        created_at=room.created_at,
        started_at=room.started_at,
        stream_key=room.stream_key,
        rtmp_url=room.rtmp_url,
        hls_url=room.hls_url,
        flv_url=room.flv_url
    )


@router.get("/stream-url", response_model=StreamUrlResponse)
async def get_stream_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取推流地址（仅主播可见）"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.user_id == current_user.id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在，请先创建直播间"
        )
    
    push_url = f"{room.rtmp_url}/{room.stream_key}"
    
    return StreamUrlResponse(
        rtmp_url=room.rtmp_url,
        stream_key=room.stream_key,
        push_url=push_url,
        hls_url=room.hls_url,
        flv_url=room.flv_url
    )


@router.get("/list", response_model=List[LiveRoomResponse])
async def get_live_room_list(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    only_live: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    获取直播间列表
    
    - page: 页码
    - page_size: 每页数量
    - category: 分类筛选
    - only_live: 只显示正在直播的
    """
    query = select(LiveRoom)
    
    if only_live:
        query = query.where(LiveRoom.is_live == True)
    
    if category:
        query = query.where(LiveRoom.category == category)
    
    # 按观看人数排序
    query = query.order_by(LiveRoom.viewer_count.desc())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    rooms = result.scalars().all()
    
    return [
        LiveRoomResponse(
            id=room.id,
            room_id=room.room_id,
            title=room.title,
            description=room.description,
            anchor_name=room.anchor_name,
            status=room.status,
            is_live=room.is_live,
            viewer_count=room.viewer_count,
            total_viewers=room.total_viewers,
            like_count=room.like_count,
            cover_image=room.cover_image,
            category=room.category,
            created_at=room.created_at,
            started_at=room.started_at,
            hls_url=room.hls_url,
            flv_url=room.flv_url
        )
        for room in rooms
    ]


@router.get("/{room_id}", response_model=LiveRoomResponse)
async def get_live_room(
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定直播间信息"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.room_id == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在"
        )
    
    return LiveRoomResponse(
        id=room.id,
        room_id=room.room_id,
        title=room.title,
        description=room.description,
        anchor_name=room.anchor_name,
        status=room.status,
        is_live=room.is_live,
        viewer_count=room.viewer_count,
        total_viewers=room.total_viewers,
        like_count=room.like_count,
        cover_image=room.cover_image,
        category=room.category,
        created_at=room.created_at,
        started_at=room.started_at,
        hls_url=room.hls_url,
        flv_url=room.flv_url
    )


@router.post("/start")
async def start_live(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """开始直播"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.user_id == current_user.id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在"
        )
    
    # 检查直播类型
    if room.source_type == "self":
        # 自己推流的情况，提示用户需要使用OBS
        if not room.flv_url or "your-domain" in room.flv_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先配置直播服务器地址，或使用外部直播源。如需使用OBS推流，请联系管理员配置直播服务器。"
            )
    elif room.source_type == "external":
        # 外部直播源，检查是否配置了地址
        if not room.source_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先配置外部直播源地址"
            )
    
    room.is_live = True
    room.status = "online"
    room.started_at = datetime.now()
    
    await db.commit()
    
    return {"message": "直播已开始", "room_id": room.room_id}


@router.post("/stop")
async def stop_live(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """结束直播"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.user_id == current_user.id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在"
        )
    
    room.is_live = False
    room.status = "offline"
    room.ended_at = datetime.now()
    room.viewer_count = 0
    
    await db.commit()
    
    return {"message": "直播已结束", "room_id": room.room_id}


class UpdateLiveRoomRequest(BaseModel):
    """更新直播间请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None


@router.put("/update")
async def update_live_room(
    request: UpdateLiveRoomRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新直播间配置"""
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.user_id == current_user.id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播间不存在"
        )
    
    # 更新字段
    if request.title is not None:
        room.title = request.title
    if request.description is not None:
        room.description = request.description
    if request.category is not None:
        room.category = request.category
    if request.source_type is not None:
        room.source_type = request.source_type
    if request.source_url is not None:
        room.source_url = request.source_url
    
    await db.commit()
    await db.refresh(room)
    
    return {
        "message": "直播间配置已更新",
        "room": LiveRoomResponse(
            id=room.id,
            room_id=room.room_id,
            title=room.title,
            description=room.description,
            anchor_name=room.anchor_name,
            status=room.status,
            is_live=room.is_live,
            viewer_count=room.viewer_count,
            total_viewers=room.total_viewers,
            like_count=room.like_count,
            cover_image=room.cover_image,
            category=room.category,
            source_type=room.source_type,
            source_url=room.source_url,
            created_at=room.created_at,
            started_at=room.started_at,
            stream_key=room.stream_key,
            rtmp_url=room.rtmp_url,
            hls_url=room.hls_url,
            flv_url=room.flv_url
        )
    }


# ==================== 直播带货功能 ====================

class LiveProduct(Base):
    """直播商品表"""
    __tablename__ = "live_products"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False, index=True, comment="直播间ID")
    product_name = Column(String(200), nullable=False, comment="商品名称")
    description = Column(Text, comment="商品描述")
    price = Column(String(20), nullable=False, comment="价格")
    original_price = Column(String(20), comment="原价")
    stock = Column(Integer, default=0, comment="库存")
    product_image = Column(String(500), comment="商品图片")
    purchase_link = Column(String(500), comment="购买链接")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class ProductRequest(BaseModel):
    """商品请求模型"""
    product_name: str = Field(..., description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., description="价格")
    original_price: Optional[float] = Field(None, description="原价")
    stock: int = Field(0, description="库存")
    product_image: Optional[str] = Field(None, description="商品图片URL")
    purchase_link: Optional[str] = Field(None, description="购买链接")
    sort_order: int = Field(0, description="排序")
    is_active: int = Field(1, description="上架状态: 1-上架, 0-下架")


class ProductResponse(BaseModel):
    """商品响应模型"""
    id: int
    product_name: str
    description: Optional[str]
    price: str
    original_price: Optional[str]
    stock: int
    product_image: Optional[str]
    purchase_link: Optional[str]
    is_active: bool
    sort_order: int
    created_at: datetime


@router.post("/products/add")
async def add_product(
    product: ProductRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: AsyncSessionLocal())
):
    """添加直播商品"""
    try:
        # 获取用户的直播间
        stmt = select(LiveRoom).where(LiveRoom.user_id == current_user.id)
        result = await db.execute(stmt)
        room = result.scalar_one_or_none()
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="请先创建直播间"
            )
        
        # 创建商品
        from sqlalchemy import text
        insert_sql = text("""
            INSERT INTO live_products 
            (room_id, product_name, description, price, original_price, stock, product_image, purchase_link, sort_order)
            VALUES (:room_id, :product_name, :description, :price, :original_price, :stock, :product_image, :purchase_link, :sort_order)
        """)
        
        await db.execute(insert_sql, {
            "room_id": room.id,
            "product_name": product.product_name,
            "description": product.description,
            "price": str(product.price),
            "original_price": str(product.original_price) if product.original_price else None,
            "stock": product.stock,
            "product_image": product.product_image,
            "purchase_link": product.purchase_link,
            "sort_order": product.sort_order
        })
        await db.commit()
        
        return {"success": True, "message": "商品添加成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加商品失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加商品失败: {str(e)}"
        )


@router.get("/products/{room_id}")
async def get_products(
    room_id: int,
    db: AsyncSession = Depends(lambda: AsyncSessionLocal())
):
    """获取直播间商品列表"""
    try:
        from sqlalchemy import text
        query_sql = text("""
            SELECT * FROM live_products 
            WHERE room_id = :room_id
            ORDER BY sort_order ASC, created_at DESC
        """)
        
        result = await db.execute(query_sql, {"room_id": room_id})
        products = result.fetchall()
        
        products_list = []
        for p in products:
            products_list.append({
                "id": p[0],
                "product_name": p[2],
                "description": p[3],
                "price": p[4],
                "original_price": p[5],
                "stock": p[6],
                "product_image": p[7],
                "purchase_link": p[8],
                "is_active": int(p[9]),
                "sort_order": p[10]
            })
        
        return {
            "success": True,
            "products": products_list
        }
        
    except Exception as e:
        logger.error(f"获取商品列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取商品列表失败: {str(e)}"
        )


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: AsyncSessionLocal())
):
    """删除商品"""
    try:
        from sqlalchemy import text
        # 软删除，设置is_active=0
        delete_sql = text("""
            UPDATE live_products SET is_active = 0 WHERE id = :product_id
        """)
        
        await db.execute(delete_sql, {"product_id": product_id})
        await db.commit()
        
        return {"success": True, "message": "删除成功"}
        
    except Exception as e:
        logger.error(f"删除商品失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除商品失败: {str(e)}"
        )


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product: ProductRequest,
    db: AsyncSession = Depends(lambda: AsyncSessionLocal())
):
    """更新商品信息"""
    try:
        from sqlalchemy import text
        
        logger.info(f"开始更新商品: product_id={product_id}")
        logger.info(f"商品数据: {product.dict()}")
        
        update_sql = text("""
            UPDATE live_products 
            SET product_name = :product_name,
                description = :description,
                price = :price,
                original_price = :original_price,
                stock = :stock,
                product_image = :product_image,
                purchase_link = :purchase_link,
                sort_order = :sort_order,
                is_active = :is_active,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :product_id
        """)
        
        await db.execute(update_sql, {
            "product_id": product_id,
            "product_name": product.product_name,
            "description": product.description,
            "price": str(product.price),
            "original_price": str(product.original_price) if product.original_price else None,
            "stock": product.stock,
            "product_image": product.product_image,
            "purchase_link": product.purchase_link,
            "sort_order": product.sort_order,
            "is_active": product.is_active
        })
        await db.commit()
        
        logger.info(f"商品更新成功: product_id={product_id}")
        return {"success": True, "message": "更新成功"}
        
    except Exception as e:
        logger.error(f"更新商品失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "message": f"更新失败: {str(e)}"}
