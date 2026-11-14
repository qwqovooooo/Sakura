import os
import sys
from contextlib import asynccontextmanager
import logging
import logging.config
import yaml
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Base, engine  # 导入数据库模型基类

# 配置项目路径
sys.path.append(str(Path(__file__).resolve().parent))

# 导入配置项
from app.config import settings

# 初始化日志系统
def setup_logging():
    """加载日志配置文件并应用"""
    try:
        with open('./config/logging.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"日志配置加载失败: {e}", file=sys.stderr)
        return logging.getLogger(__name__)

logger = setup_logging()

# 初始化定时任务调度器
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

# 异步数据库会话依赖
from app.config import AsyncSessionLocal

async def get_db():
    """创建异步数据库会话上下文管理器"""
    async with AsyncSessionLocal() as session:
        yield session

# 定时任务执行函数
async def run_sakura_data_update():
    """异步执行樱花数据更新任务"""
    logger.info('开始更新数据')
    from app.task.tasks import SakuarDataSchedule
    # TODO: 如果 tasks.py 中的方法需要异步化，请同步更新
    await SakuarDataSchedule().get_sakura_data()
    logger.info('数据更新完成')

# 应用生命周期管理
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """应用启动与关闭时的生命周期钩子"""
    logger.info("应用启动中...")
    
    # 异步创建数据库表结构
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化定时任务
    try:
        # 添加每日定时任务
        scheduler.add_job(
            run_sakura_data_update,
            'cron',
            id='daily_sakura_update',
            day='*',
            hour='10',
            minute='47',
            second='01',
            misfire_grace_time=60
        )
        
        # 启动调度器（带文件锁防止重复启动）
        if not os.path.exists('scheduler.lock'):
            with open('scheduler.lock', 'w'):
                pass
            scheduler.start()
    except ImportError:
        logger.warning("未找到任务模块，跳过定时任务初始化")
    except Exception as e:
        logger.error(f"定时任务启动失败: {e}")
    
    yield  # 应用运行阶段
    
    # 应用关闭清理
    logger.info("应用关闭中...")
    scheduler.shutdown()
    if os.path.exists('scheduler.lock'):
        os.remove('scheduler.lock')
    
    # 关闭数据库引擎
    await engine.dispose()

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=app_lifespan
)



# 配置跨域资源共享（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # 前端开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由模块（保留你原有所有路由）
from app.routes import auth, comment, sakura_vod_info, video_collection
from app.routes import admin_user, admin_movie, admin_comment
from app.routes import sql_agent, movie_qa, live_stream, movie_recommendation

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(comment.router, tags=["comment"])
app.include_router(sakura_vod_info.router, tags=["vod"])
app.include_router(video_collection.router, prefix="/collection", tags=["collection"])

# 管理后台路由
app.include_router(admin_user.router, prefix="/admin", tags=["admin-user"])
app.include_router(admin_movie.router, prefix="/admin", tags=["admin-movie"])
app.include_router(admin_comment.router, prefix="/admin", tags=["admin-comment"])

# SQL Agent 智能搜索路由
app.include_router(sql_agent.router, prefix="/sql-agent", tags=["sql-agent"])

# 电影问答路由
app.include_router(movie_qa.router, prefix="/movie-qa", tags=["movie-qa"])

# 直播功能路由
app.include_router(live_stream.router, prefix="/live", tags=["live-stream"])

# 智能电影推荐路由
app.include_router(movie_recommendation.router, prefix="/recommend", tags=["movie-recommendation"])

# 基础接口（保留原有）
@app.get("/")
async def root():
    return {"message": "Sakura Comic API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}