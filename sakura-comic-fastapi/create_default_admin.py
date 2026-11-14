"""
自动创建默认管理员账号
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import AsyncSessionLocal
from app.models.models import User
from sqlalchemy.future import select

async def create_default_admin():
    """创建默认管理员用户"""
    print("=" * 50)
    print("自动创建默认管理员账号")
    print("=" * 50)
    
    admin_name = "admin"
    admin_password = "admin123"
    
    try:
        async with AsyncSessionLocal() as session:
            # 检查用户是否已存在
            result = await session.execute(select(User).filter(User.name == admin_name))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # 更新为管理员
                existing_user.is_admin = True
                existing_user.set_password(admin_password)
                await session.commit()
                print(f"\n✅ 用户 '{admin_name}' 已存在，已更新为管理员权限")
            else:
                # 创建新管理员
                admin_user = User(
                    name=admin_name,
                    is_admin=True
                )
                admin_user.set_password(admin_password)
                
                session.add(admin_user)
                await session.commit()
                print(f"\n✅ 默认管理员用户创建成功！")
            
            print(f"\n管理员登录信息：")
            print(f"  用户名: {admin_name}")
            print(f"  密码: {admin_password}")
            print(f"\n管理后台地址: http://localhost:3001/#/admin/login")
            print(f"\n请登录后修改密码！")
            
    except Exception as e:
        print(f"\n❌ 创建管理员失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_default_admin())
