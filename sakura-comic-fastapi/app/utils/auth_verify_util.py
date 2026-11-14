import datetime
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..config import settings, AsyncSessionLocal
from ..models.models import User

async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session

# 创建安全方案
security = HTTPBearer(scheme_name="JWT")

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_DAYS = settings.ACCESS_TOKEN_EXPIRE_DAYS

def generate_auth_token(user_id: int, name: str, effective_time: int = 30, **kwargs):
    """
    生成用于登录认证的JWT
    """
    # 计算过期时间
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=effective_time)
    
    # 创建token数据
    to_encode = {
        "id": user_id,
        "name": name,
        "dead_time": expire.strftime("%Y-%m-%d"),
        "exp": expire  # 添加过期时间
    }
    to_encode.update(**kwargs)
    
    # 编码token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def parse_user_from_token(token: str) -> dict:
    """
    从token中解析用户信息
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    """
    异步获取当前登录用户
    """
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解析token
        logger.info(f"Token: {credentials.credentials[:50]}...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token payload: {payload}")
        
        # 检查过期时间
        dead_time_str = payload.get("dead_time")
        if not dead_time_str:
            logger.error("未找到dead_time字段")
            raise credentials_exception
        
        # 将日期字符串转换为日期对象，并设置为当天末尾（23:59:59）
        dead_time = datetime.datetime.strptime(dead_time_str, "%Y-%m-%d")
        dead_time = dead_time.replace(hour=23, minute=59, second=59)
        
        now = datetime.datetime.now()
        logger.info(f"Token过期时间: {dead_time}, 当前时间: {now}")
        
        if dead_time < now:
            logger.error(f"Token已过期: {dead_time} < {now}")
            raise credentials_exception
        
        # 获取用户信息
        user_id: int = payload.get("id")
        if user_id is None:
            logger.error("未找到用户ID")
            raise credentials_exception
            
        logger.info(f"查询用户ID: {user_id}")
    except (JWTError, ValueError) as e:
        logger.error(f"Token验证失败: {e}")
        raise credentials_exception
    
    # 异步查询用户
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        logger.error(f"未找到用户: {user_id}")
        raise credentials_exception
    
    logger.info(f"用户验证成功: {user.name} (ID: {user.id})")
    return user

async def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """
    获取当前登录用户的ID
    """
    return current_user.id