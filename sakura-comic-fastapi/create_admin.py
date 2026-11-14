"""
创建管理员用户脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import AsyncSessionLocal
from app.models.models import User
from sqlalchemy.future import select

async def create_admin_user():
    """创建管理员用户"""
    print("=" * 50)
    print("创建管理员用户")
    print("=" * 50)
    
    # 获取管理员信息
    admin_name = input("请输入管理员用户名（默认：admin）: ").strip() or "admin"
    admin_password = input("请输入管理员密码（默认：admin123）: ").strip() or "admin123"
    
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
                print(f"\n✅ 管理员用户 '{admin_name}' 创建成功！")
            
            print(f"\n管理员信息：")
            print(f"  用户名: {admin_name}")
            print(f"  密码: {admin_password}")
            print(f"\n请妥善保管管理员账号信息！")
            
    except Exception as e:
        print(f"\n❌ 创建管理员失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
