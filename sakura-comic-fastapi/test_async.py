#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步功能测试脚本
测试数据库连接和基本查询是否正常工作
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import AsyncSessionLocal, engine, Base
from app.models.models import User, MovDetail, MovType
from sqlalchemy.future import select

async def test_database_connection():
    """测试异步数据库连接"""
    print("=" * 50)
    print("测试异步数据库连接")
    print("=" * 50)
    
    try:
        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功")
        
        # 测试数据库查询
        async with AsyncSessionLocal() as session:
            # 查询用户数量
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"✅ 用户表查询成功，共有 {len(users)} 个用户")
            
            # 查询视频类型数量
            result = await session.execute(select(MovType))
            types = result.scalars().all()
            print(f"✅ 视频类型查询成功，共有 {len(types)} 个类型")
            
            # 查询视频详情数量
            result = await session.execute(select(MovDetail))
            movies = result.scalars().all()
            print(f"✅ 视频详情查询成功，共有 {len(movies)} 个视频")
        
        print("\n✅ 所有异步数据库操作测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭引擎
        await engine.dispose()

async def test_user_model():
    """测试 User 模型的异步方法"""
    print("\n" + "=" * 50)
    print("测试 User 模型异步方法")
    print("=" * 50)
    
    try:
        async with AsyncSessionLocal() as session:
            # 测试 get_by_name 方法
            user = await User.get_by_name(session, "test_user")
            if user:
                print(f"✅ 找到用户: {user.name}")
            else:
                print("ℹ️  未找到名为 'test_user' 的用户（这是正常的）")
        
        print("✅ User 模型异步方法测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ User 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("\n🚀 开始异步功能测试...\n")
    
    # 测试数据库连接
    db_test = await test_database_connection()
    
    # 测试用户模型
    user_test = await test_user_model()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"数据库连接测试: {'✅ 通过' if db_test else '❌ 失败'}")
    print(f"User 模型测试: {'✅ 通过' if user_test else '❌ 失败'}")
    
    if db_test and user_test:
        print("\n🎉 所有测试通过！异步重构成功！")
        print("\n可以使用以下命令启动服务:")
        print("  python run.py")
        print("  或")
        print("  uvicorn main:app --reload")
    else:
        print("\n⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main())
