from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# 导入内部模块
from ..models.models import User
from ..utils.auth_verify_util import generate_auth_token, get_current_user
from ..config import AsyncSessionLocal

# 异步数据库会话依赖
async def get_db():
    """创建并返回异步数据库会话，自动关闭连接"""
    async with AsyncSessionLocal() as session:
        yield session

# 初始化路由（保留原有）
router = APIRouter()

# ------------------------------
# 数据模型定义（保留原有，注意字段名是 name/password）
# ------------------------------
class LoginRequest(BaseModel):
    """登录请求参数模型"""
    name: str
    password: str

class RegisterRequest(BaseModel):
    """注册请求参数模型"""
    name: str
    password: str

# ------------------------------
# 接口实现（核心修复登录逻辑）
# ------------------------------
@router.post("/login", response_model=dict)
async def user_login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录接口：验证账号密码并返回令牌"""
    # 异步查询用户
    user = await User.get_by_name(db, login_data.name)
    
    # 核心修复：增加用户不存在的明确判断（原有逻辑可能漏了这步）
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "data": {
                    "code": 400,
                    "message": "登录失败, 用户名不存在"
                }
            }
        )
    
    # 验证密码（保留原有 validate_password 方法，确保加密逻辑一致）
    if not user.validate_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "data": {
                    "code": 400,
                    "message": "登录失败, 账户或密码不正确"
                }
            }
        )
    
    # 生成JWT令牌（保留原有逻辑）
    token = generate_auth_token(user_id=user.id, name=user.name)
    return {
        "data": {
            "code": 200,
            "message": "Login successfully",
            "token": f"jwt {token}",
            "user_id": user.id,
            "user_name": user.name
        }
    }

@router.post("/register", response_model=dict)
async def user_register(register_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册接口：创建新用户并检查用户名唯一性"""
    # 异步检查用户名是否已存在
    existing_user = await User.get_by_name(db, register_data.name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "data": {
                    "code": 400,
                    "message": "注册失败, 当前用户名已被注册, 请更换用户名"
                }
            }
        )
    
    # 创建新用户（保留原有 set_password 加密逻辑）
    new_user = User(name=register_data.name)
    new_user.set_password(register_data.password)  # 加密存储密码
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {
            "data": {
                "code": 200,
                "message": "注册成功, 请重新登录"
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "data": {
                    "code": 500,
                    "message": f"注册失败, 服务器内部错误: {str(e)}"  # 增加错误信息便于调试
                }
            }
        )

@router.post("/user", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息：需有效令牌"""
    return {
        "data": {
            "code": 200,
            "message": "获取用户信息成功",
            "data": {
                "id": current_user.id,
                "name": current_user.name,
                "is_admin": current_user.is_admin  # 添加管理员字段
            }
        }
    }

@router.get("/api/check", response_model=dict)
async def verify_token_validity(current_user: User = Depends(get_current_user)):
    """验证令牌有效性：令牌有效则返回成功"""
    return {
        "data": {
            "message": "success"
        }
    }