#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试数据脚本
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import AsyncSessionLocal
from app.models.models import MovDetail

async def add_test_data():
    """
    添加测试数据
    """
    print("开始添加测试数据...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已有数据
            from sqlalchemy import select
            result = await db.execute(select(MovDetail))
            existing_movies = result.fetchall()
            
            if existing_movies:
                print(f"数据库中已存在 {len(existing_movies)} 条电影数据，跳过添加测试数据")
                return
            
            # 添加一些测试电影数据
            test_movies = [
                {
                    "vod_id": 1,
                    "type_id": 1,  # 电影
                    "type_name": "电影",
                    "vod_name": "测试电影1",
                    "vod_pic": "https://via.placeholder.com/300x400/FF6B6B/FFFFFF?text=电影1",
                    "vod_remarks": "高清",
                    "vod_content": "这是一部测试电影",
                    "vod_play_url": "第1集$http://example.com/video1.mp4",
                    "vod_play_from": "测试源",
                    "vod_area": "中国",
                    "vod_year": "2023",
                    "vod_director": "测试导演",
                    "vod_actor": "测试演员",
                    "vod_time": datetime.now(),
                    "vod_score": "8.5",
                    "vod_hits": 100
                },
                {
                    "vod_id": 2,
                    "type_id": 1,  # 电影
                    "type_name": "电影",
                    "vod_name": "测试电影2",
                    "vod_pic": "https://via.placeholder.com/300x400/4ECDC4/FFFFFF?text=电影2",
                    "vod_remarks": "蓝光",
                    "vod_content": "这是一部测试电影2",
                    "vod_play_url": "第1集$http://example.com/video2.mp4",
                    "vod_play_from": "测试源",
                    "vod_area": "美国",
                    "vod_year": "2022",
                    "vod_director": "测试导演2",
                    "vod_actor": "测试演员2",
                    "vod_time": datetime.now(),
                    "vod_score": "7.8",
                    "vod_hits": 200
                },
                {
                    "vod_id": 3,
                    "type_id": 2,  # 电视剧
                    "type_name": "电视剧",
                    "vod_name": "测试电视剧1",
                    "vod_pic": "https://via.placeholder.com/300x400/45B7D1/FFFFFF?text=电视剧1",
                    "vod_remarks": "更新至10集",
                    "vod_content": "这是一部测试电视剧",
                    "vod_play_url": "第1集$http://example.com/video3.mp4",
                    "vod_play_from": "测试源",
                    "vod_area": "韩国",
                    "vod_year": "2023",
                    "vod_director": "测试导演3",
                    "vod_actor": "测试演员3",
                    "vod_time": datetime.now(),
                    "vod_score": "9.0",
                    "vod_hits": 150
                },
                {
                    "vod_id": 4,
                    "type_id": 4,  # 动漫
                    "type_name": "动漫",
                    "vod_name": "测试动漫1",
                    "vod_pic": "https://via.placeholder.com/300x400/96CEB4/FFFFFF?text=动漫1",
                    "vod_remarks": "连载中",
                    "vod_content": "这是一部测试动漫",
                    "vod_play_url": "第1集$http://example.com/video4.mp4",
                    "vod_play_from": "测试源",
                    "vod_area": "日本",
                    "vod_year": "2023",
                    "vod_director": "测试导演4",
                    "vod_actor": "测试演员4",
                    "vod_time": datetime.now(),
                    "vod_score": "8.2",
                    "vod_hits": 300
                },
                {
                    "vod_id": 5,
                    "type_id": 3,  # 综艺
                    "type_name": "综艺",
                    "vod_name": "测试综艺1",
                    "vod_pic": "https://via.placeholder.com/300x400/FFEAA7/000000?text=综艺1",
                    "vod_remarks": "最新一期",
                    "vod_content": "这是一档测试综艺节目",
                    "vod_play_url": "第1期$http://example.com/video5.mp4",
                    "vod_play_from": "测试源",
                    "vod_area": "中国",
                    "vod_year": "2023",
                    "vod_director": "测试导演5",
                    "vod_actor": "测试嘉宾5",
                    "vod_time": datetime.now(),
                    "vod_score": "7.5",
                    "vod_hits": 250
                }
            ]
            
            for movie_data in test_movies:
                movie = MovDetail(**movie_data)
                db.add(movie)
            
            await db.commit()
            print(f"成功添加了 {len(test_movies)} 条测试电影数据")
            
        except Exception as e:
            await db.rollback()
            print(f"添加测试数据失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_test_data())