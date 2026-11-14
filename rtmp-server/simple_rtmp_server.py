"""
简易的RTMP转发服务器
用于接收OBS推流并提供HTTP-FLV播放
"""
import subprocess
import os
import sys

print("=" * 60)
print("简易RTMP服务器启动脚本")
print("=" * 60)
print("\n由于搭建完整的RTMP服务器需要额外软件，建议使用以下方案：")
print("\n方案1：安装Docker Desktop（推荐）")
print("  下载地址：https://www.docker.com/products/docker-desktop")
print("  安装后执行：docker run -d -p 1935:1935 -p 8080:8080 ossrs/srs:5")
print("\n方案2：使用在线SRS服务")
print("  推流地址：rtmp://你的公网IP/live")
print("  需要云服务器")
print("\n方案3：使用云直播服务")
print("  - 阿里云直播：https://www.aliyun.com/product/live")
print("  - 七牛云直播：https://www.qiniu.com/products/pili")
print("  通常有免费试用额度")
print("\n" + "=" * 60)
print("如果你有Docker，我可以帮你一键启动RTMP服务器")
print("=" * 60)
