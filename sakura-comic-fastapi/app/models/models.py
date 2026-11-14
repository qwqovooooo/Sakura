import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from ..config import settings, Base

# 创建密码上下文
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class MovType(Base):
    __tablename__ = 'sakura_movtype'
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(20), nullable=False)
    
    # 关系
    this_type_movies = relationship('MovInfo', back_populates='this_mov_type')
    this_type_movie_details = relationship('MovDetail', back_populates='this_mov_type')

class MovInfo(Base):
    __tablename__ = 'sakura_movinfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('sakura_movtype.type_id'))
    type_name = Column(String(20), nullable=False)
    vod_en = Column(Text, nullable=False)
    vod_id = Column(Integer, unique=True, nullable=False)
    vod_name = Column(Text, nullable=False)
    vod_play_from = Column(Text)
    vod_remarks = Column(Text)
    vod_time = Column(DateTime)
    
    # 关系
    this_mov_type = relationship('MovType', back_populates='this_type_movies')

class MovDetail(Base):
    __tablename__ = 'sakura_movdetail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer)
    type_id = Column(Integer, ForeignKey('sakura_movtype.type_id'))
    type_id_1 = Column(Integer)
    type_name = Column(String(20))
    vod_actor = Column(Text)
    vod_area = Column(Text)
    vod_author = Column(Text)
    vod_behind = Column(Text)
    vod_blurb = Column(Text)
    vod_class = Column(Text)
    vod_color = Column(Text)
    vod_content = Column(Text)
    vod_copyright = Column(Integer)
    vod_director = Column(Text)
    vod_douban_id = Column(Integer)
    vod_douban_score = Column(String(20))
    vod_down = Column(Integer)
    vod_down_from = Column(Text)
    vod_down_note = Column(Text)
    vod_down_server = Column(Text)
    vod_down_url = Column(Text)
    vod_duration = Column(Text)
    vod_en = Column(Text)
    vod_hits = Column(Integer)
    vod_hits_day = Column(Integer)
    vod_hits_month = Column(Integer)
    vod_hits_week = Column(Integer)
    vod_id = Column(Integer, unique=True, nullable=False)
    vod_isend = Column(Integer)
    vod_jumpurl = Column(Text)
    vod_lang = Column(Text)
    vod_letter = Column(Text)
    vod_level = Column(Integer)
    vod_lock = Column(Integer)
    vod_name = Column(Text)
    vod_pic = Column(Text)
    vod_pic_screenshot = Column(Text)
    vod_pic_slide = Column(Text)
    vod_pic_thumb = Column(Text)
    vod_play_from = Column(Text)
    vod_play_note = Column(Text)
    vod_play_server = Column(Text)
    vod_play_url = Column(Text)
    vod_plot = Column(Integer)
    vod_plot_detail = Column(Text)
    vod_plot_name = Column(Text)
    vod_points = Column(Integer)
    vod_points_down = Column(Integer)
    vod_points_play = Column(Integer)
    vod_pubdate = Column(Text)
    vod_pwd = Column(Text)
    vod_pwd_down = Column(Text)
    vod_pwd_down_url = Column(Text)
    vod_pwd_play = Column(Text)
    vod_pwd_play_url = Column(Text)
    vod_pwd_url = Column(Text)
    vod_rel_art = Column(Text)
    vod_rel_vod = Column(Text)
    vod_remarks = Column(Text)
    vod_reurl = Column(Text)
    vod_score = Column(Text)
    vod_score_all = Column(Integer)
    vod_score_num = Column(Integer)
    vod_serial = Column(Text)
    vod_state = Column(Text)
    vod_status = Column(Integer)
    vod_sub = Column(Text)
    vod_tag = Column(Text)
    vod_time = Column(DateTime)
    vod_time_add = Column(Integer)
    vod_time_hits = Column(Integer)
    vod_time_make = Column(Integer)
    vod_total = Column(Integer)
    vod_tpl = Column(Text)
    vod_tpl_down = Column(Text)
    vod_tpl_play = Column(Text)
    vod_trysee = Column(Integer)
    vod_tv = Column(Text)
    vod_up = Column(Integer)
    vod_version = Column(Text)
    vod_weekday = Column(Text)
    vod_writer = Column(Text)
    vod_year = Column(Text)
    
    # 关系
    this_mov_type = relationship('MovType', back_populates='this_type_movie_details')
    comments = relationship('Comment', back_populates='mov_detail', cascade='all, delete-orphan')

class User(Base):
    __tablename__ = 'sakura_user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, index=True)
    password_hash = Column(String(128))
    is_admin = Column(Boolean, default=False)  # 管理员标识
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # 创建时间
    
    # 关系
    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    collections = relationship('UserCollection', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        # 生成hash后的密码
        self.password_hash = pwd_context.hash(password)
    
    def validate_password(self, password):
        # 验证密码
        return pwd_context.verify(password, self.password_hash)
    
    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str):
        """异步查询用户"""
        result = await db.execute(select(cls).filter(cls.name == name))
        return result.scalar_one_or_none()

class Comment(Base):
    __tablename__ = 'sakura_comment'
    id = Column(Integer, primary_key=True)
    body = Column(Text)
    reviewed = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    user_id = Column(Integer, ForeignKey('sakura_user.id'))
    replied_id = Column(Integer, ForeignKey('sakura_comment.id'))
    movdetail_id = Column(Integer, ForeignKey('sakura_movdetail.id'))
    
    # 关系
    user = relationship('User', back_populates='comments')
    mov_detail = relationship('MovDetail', back_populates='comments')
    replies = relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = relationship('Comment', back_populates='replies', remote_side=[id])

class UserCollection(Base):
    __tablename__ = 'sakura_user_collection'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('sakura_user.id'))
    movdetail_id_list = Column(Text, default='')
    
    # 关系
    user = relationship('User', back_populates='collections')
    
    def add_vod_id(self, vod_id: str):
        # 添加视频ID到收藏列表
        if not self.movdetail_id_list:
            self.movdetail_id_list = ''
        if vod_id + ';' not in self.movdetail_id_list:
            self.movdetail_id_list += vod_id + ';'