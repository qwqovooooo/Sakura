import logging
import requests
import pymysql
from dotenv import load_dotenv
import os
import time
import json

logger = logging.getLogger(__name__)

load_dotenv()
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/movie')
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

class SakuraData:
    """
    樱花动漫数据爬虫
    """
    
    def __init__(self):
        # 数据库连接
        self.conn = pymysql.connect(
            host=host_db[0],
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else '',
            database=host_db[1] if len(host_db) > 1 else 'movie',
            autocommit=False,
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        
        # 使用更稳定的资源站API
        # 备用API列表（可以切换尝试）
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
            self.cursor.execute("SELECT vod_id FROM sakura_movdetail WHERE vod_id = %s", (vod_id,))
            existing = self.cursor.fetchone()
            
            # 准备数据
            vod_name = movie.get('vod_name', '')
            vod_pic = movie.get('vod_pic', '')
            vod_remarks = movie.get('vod_remarks', '')
            vod_score = movie.get('vod_score', '0')
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
            
            if existing:
                # 更新
                sql = """
                    UPDATE sakura_movdetail 
                    SET vod_name=%s, vod_pic=%s, vod_remarks=%s, vod_score=%s,
                        vod_year=%s, vod_area=%s, vod_class=%s, vod_director=%s,
                        vod_actor=%s, vod_content=%s, vod_play_from=%s, vod_play_url=%s,
                        type_id=%s, type_name=%s
                    WHERE vod_id=%s
                """
                self.cursor.execute(sql, (
                    vod_name, vod_pic, vod_remarks, vod_score,
                    vod_year, vod_area, vod_class, vod_director,
                    vod_actor, vod_content, vod_play_from, vod_play_url,
                    type_id, type_name, vod_id
                ))
                print(f"  更新: {vod_name}")
            else:
                # 插入
                sql = """
                    INSERT INTO sakura_movdetail 
                    (vod_id, vod_name, vod_pic, vod_remarks, vod_score,
                     vod_year, vod_area, vod_class, vod_director, vod_actor,
                     vod_content, vod_play_from, vod_play_url, type_id, type_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (
                    vod_id, vod_name, vod_pic, vod_remarks, vod_score,
                    vod_year, vod_area, vod_class, vod_director, vod_actor,
                    vod_content, vod_play_from, vod_play_url, type_id, type_name
                ))
                print(f"  新增: {vod_name}")
            
            return True
            
        except Exception as e:
            print(f"保存失败 {movie.get('vod_name', '未知')}: {e}")
            return False

class SakuarDataSchedule:
    """
    樱花动漫数据定时更新任务
    """
    
    def __init__(self):
        self.db = SessionLocal()
        # 这里可以根据需要初始化其他参数
    
    def __del__(self):
        # 确保数据库会话关闭
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_sakura_data(self):
        """
        获取樱花动漫数据
        注：这里是一个示例实现，实际的爬虫逻辑可能需要根据具体网站进行调整
        """
        try:
            logger.info("开始获取樱花动漫数据")
            
            # 这里应该实现实际的爬虫逻辑
            # 由于原项目中没有提供具体的爬虫实现，这里提供一个框架
            
            # 1. 获取视频类型数据
            self._get_mov_types()
            
            # 2. 获取视频信息数据
            self._get_mov_info()
            
            # 3. 获取视频详情数据
            self._get_mov_detail()
            
            logger.info("樱花动漫数据获取完成")
            
        except Exception as e:
            logger.error(f"获取樱花动漫数据失败: {str(e)}")
            if hasattr(self, 'db'):
                self.db.rollback()
    
    def _get_mov_types(self):
        """
        获取视频类型数据
        """
        try:
            # 示例：假设从某个接口或网站获取类型数据
            # 这里应该替换为实际的爬虫逻辑
            logger.info("获取视频类型数据")
            
            # 示例类型数据
            types = [
                {"type_id": 1, "type_name": "动漫"},
                {"type_id": 2, "type_name": "电影"},
                {"type_id": 3, "type_name": "电视剧"},
                {"type_id": 4, "type_name": "综艺"},
                {"type_id": 5, "type_name": "纪录片"}
            ]
            
            # 保存到数据库
            for type_data in types:
                existing_type = self.db.query(MovType).filter(
                    MovType.type_id == type_data["type_id"]
                ).first()
                
                if existing_type:
                    # 更新现有类型
                    existing_type.type_name = type_data["type_name"]
                else:
                    # 创建新类型
                    new_type = MovType(**type_data)
                    self.db.add(new_type)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"获取视频类型数据失败: {str(e)}")
            raise
    
    def _get_mov_info(self):
        """
        获取视频信息数据
        """
        try:
            logger.info("获取视频信息数据")
            
            # 这里应该实现实际的爬虫逻辑
            # 例如：
            # 1. 发送请求获取页面
            # 2. 解析页面内容
            # 3. 提取视频信息
            # 4. 保存到数据库
            
            # 由于没有具体的网站信息，这里只是一个框架
            
        except Exception as e:
            logger.error(f"获取视频信息数据失败: {str(e)}")
            raise
    
    def _get_mov_detail(self):
        """
        获取视频详情数据
        """
        try:
            logger.info("获取视频详情数据")
            
            # 这里应该实现实际的爬虫逻辑
            # 例如：
            # 1. 获取所有视频ID
            # 2. 遍历ID获取每个视频的详细信息
            # 3. 保存到数据库
            
            # 由于没有具体的网站信息，这里只是一个框架
            
        except Exception as e:
            logger.error(f"获取视频详情数据失败: {str(e)}")
            raise
    
    def _save_to_database(self, data, model_class):
        """
        保存数据到数据库的通用方法
        """
        try:
            # 根据具体的数据结构实现保存逻辑
            pass
        except Exception as e:
            logger.error(f"保存数据到数据库失败: {str(e)}")
            raise