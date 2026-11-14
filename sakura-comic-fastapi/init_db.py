#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""
import os
import sys
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import engine, Base
from app.models.models import *

def init_database():
    """
    初始化数据库
    """
    print("开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 初始化基础数据（如果需要）
    from main import SessionLocal
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        mov_type_count = db.query(MovType).count()
        if mov_type_count == 0:
            # 添加默认的视频类型
            default_types = [
                MovType(type_id=1, type_name="动漫"),
                MovType(type_id=2, type_name="电影"),
                MovType(type_id=3, type_name="电视剧"),
                MovType(type_id=4, type_name="综艺"),
                MovType(type_id=5, type_name="纪录片")
            ]
            db.add_all(default_types)
            db.commit()
            print("默认视频类型添加完成")
        else:
            print("数据库中已存在视频类型数据，跳过初始化")
    
    except Exception as e:
        print(f"初始化数据失败: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database()