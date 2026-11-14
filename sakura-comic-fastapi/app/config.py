from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

class Settings(BaseSettings):
    # 基本配置
    APP_NAME: str = "Sakura Comic API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sakura.db"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    
    # 日志配置
    LOGGING_PATH: str = "./logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# 创建异步数据库引擎
# 根据数据库类型选择适当的驱动
if settings.DATABASE_URL.startswith('mysql+pymysql://'):
    async_database_url = settings.DATABASE_URL.replace('mysql+pymysql://', 'mysql+aiomysql://')
    engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True  # MySQL 连接检查
    )
elif settings.DATABASE_URL.startswith('sqlite://'):
    # 对于SQLite，使用aiosqlite驱动
    sqlite_database_url = settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
    engine = create_async_engine(
        sqlite_database_url,
        echo=settings.DEBUG,
        future=True
    )
else:
    async_database_url = settings.DATABASE_URL
    engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建数据库模型基类
Base = declarative_base()