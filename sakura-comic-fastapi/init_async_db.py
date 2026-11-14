#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import engine, Base
from app.models.models import MovDetail, MovType

async def init_database():
    """
    异步初始化数据库
    """
    print("开始初始化数据库...")
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成")
    
    # 初始化基础数据（如果需要）
    async with engine.connect() as conn:
        # 开始事务
        trans = await conn.begin()
        try:
            # 检查是否已有类型数据
            from sqlalchemy import select
            result = await conn.execute(select(MovType))
            existing_types = result.fetchall()
            
            if not existing_types:
                # 添加默认的视频类型
                from sqlalchemy import insert
                default_types = [
                    {"type_id": 1, "type_name": "电影"},
                    {"type_id": 2, "type_name": "电视剧"},
                    {"type_id": 3, "type_name": "综艺"},
                    {"type_id": 4, "type_name": "动漫"},
                    {"type_id": 5, "type_name": "纪录片"}
                ]
                
                for type_data in default_types:
                    await conn.execute(insert(MovType).values(**type_data))
                
                await trans.commit()
                print("默认视频类型添加完成")
            else:
                print("数据库中已存在视频类型数据，跳过初始化")
                await trans.rollback()
        except Exception as e:
            await trans.rollback()
            print(f"初始化数据失败: {str(e)}")
    
    print("数据库初始化完成")

if __name__ == "__main__":
    asyncio.run(init_database())