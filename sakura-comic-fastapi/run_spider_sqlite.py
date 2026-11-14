#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库爬虫脚本
"""
import sys
import os
import requests
import sqlite3
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SakuraSpider:
    """
    樱花动漫数据爬虫（SQLite版本）
    """
    
    def __init__(self, db_path='sakura.db'):
        # SQLite数据库连接
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 使用稳定的资源站API
        self.api_urls = [
            "https://api.apibdzy.com/api.php/provide/vod/",  # 八戒资源（有封面）
            "https://www.hongniuzyw.com/api.php/provide/vod/",
            "https://bdzym3u8.com/api.php/provide/vod/",
        ]
        self.api_url = self.api_urls[0]  # 默认使用第一个
        
    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def get_mov_detail(self, page=1):
        """
        获取影片详情数据
        """
        try:
            print(f"正在请求第 {page} 页数据...")
            
            params = {
                'ac': 'detail',
                'pg': page
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.api_url, params=params, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return
            
            # 解析JSON数据
            data = response.json()
            
            if 'list' not in data:
                print("没有找到数据列表")
                return
            
            movies = data['list']
            print(f"获取到 {len(movies)} 条数据")
            
            # 保存到数据库
            saved_count = 0
            for movie in movies:
                if self.save_movie(movie):
                    saved_count += 1
            
            self.conn.commit()
            print(f"成功保存 {saved_count} 条数据")
            
            # 避免请求太频繁
            time.sleep(2)
            
        except Exception as e:
            print(f"爬取失败: {e}")
            self.conn.rollback()
            raise
    
    def save_movie(self, movie):
        """
        保存单个影片数据
        """
        try:
            # 检查是否已存在
            vod_id = movie.get('vod_id')
            self.cursor.execute("SELECT vod_id FROM sakura_movdetail WHERE vod_id = ?", (vod_id,))
            existing = self.cursor.fetchone()
            
            # 准备数据
            vod_name = movie.get('vod_name', '')
            vod_pic = movie.get('vod_pic', '')
            vod_remarks = movie.get('vod_remarks', '')
            vod_score = str(movie.get('vod_score', '0'))
            vod_year = movie.get('vod_year', '')
            vod_area = movie.get('vod_area', '')
            vod_class = movie.get('vod_class', '')
            vod_director = movie.get('vod_director', '')
            vod_actor = movie.get('vod_actor', '')
            vod_content = movie.get('vod_content', '')
            vod_play_from = movie.get('vod_play_from', '')
            vod_play_url = movie.get('vod_play_url', '')
            type_id = movie.get('type_id', 0)
            type_name = movie.get('type_name', '')
            vod_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if existing:
                # 更新
                sql = """
                    UPDATE sakura_movdetail 
                    SET vod_name=?, vod_pic=?, vod_remarks=?, vod_score=?,
                        vod_year=?, vod_area=?, vod_class=?, vod_director=?,
                        vod_actor=?, vod_content=?, vod_play_from=?, vod_play_url=?,
                        type_id=?, type_name=?, vod_time=?
                    WHERE vod_id=?
                """
                self.cursor.execute(sql, (
                    vod_name, vod_pic, vod_remarks, vod_score,
                    vod_year, vod_area, vod_class, vod_director,
                    vod_actor, vod_content, vod_play_from, vod_play_url,
                    type_id, type_name, vod_time, vod_id
                ))
                print(f"  更新: {vod_name}")
            else:
                # 插入
                sql = """
                    INSERT INTO sakura_movdetail 
                    (vod_id, vod_name, vod_pic, vod_remarks, vod_score,
                     vod_year, vod_area, vod_class, vod_director, vod_actor,
                     vod_content, vod_play_from, vod_play_url, type_id, type_name, vod_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(sql, (
                    vod_id, vod_name, vod_pic, vod_remarks, vod_score,
                    vod_year, vod_area, vod_class, vod_director, vod_actor,
                    vod_content, vod_play_from, vod_play_url, type_id, type_name, vod_time
                ))
                print(f"  新增: {vod_name}")
            
            return True
            
        except Exception as e:
            print(f"保存失败 {movie.get('vod_name', '未知')}: {e}")
            return False

def main():
    print("=" * 60)
    print("开始爬取影视资源数据（SQLite版本）")
    print("=" * 60)
    
    spider = SakuraSpider()
    
    # 爬取前100页（每页约20条数据，共约2000条数据）
    # 您可以根据需要调整页数
    page_count = 100
    
    for i in range(1, page_count + 1):
        print(f"\n正在爬取第 {i} 页...")
        try:
            spider.get_mov_detail(i)
            print(f"✓ 第 {i} 页爬取完成")
        except Exception as e:
            print(f"× 第 {i} 页爬取失败: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"数据爬取完成！共爬取 {page_count} 页")
    print("=" * 60)

if __name__ == '__main__':
    main()
