#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sakura Comic FastAPI 运行脚本
"""
import os
import sys
import uvicorn

def setup_environment():
    """配置运行环境，确保必要目录存在"""
    # 获取当前脚本所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 将项目根目录加入Python路径
    sys.path.append(current_dir)
    
    # 检查并创建日志目录
    log_dir = os.path.join(current_dir, "logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 检查并创建静态文件目录
    static_dir = os.path.join(current_dir, "static", "imgs")
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir, exist_ok=True)

def start_server():
    """启动FastAPI服务"""
    print("正在启动 FastAPI 应用...")
    print("服务地址: http://127.0.0.1:8000")
    print("API文档地址: http://127.0.0.1:8000/docs")
    
    
    # 启动uvicorn服务器
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式启用热重载
        log_level="info"
    )

if __name__ == "__main__":
    setup_environment()
    start_server()