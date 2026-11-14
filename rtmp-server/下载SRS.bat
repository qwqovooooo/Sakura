@echo off
echo ============================================================
echo SRS RTMP服务器下载脚本
echo ============================================================
echo.
echo 请手动下载SRS服务器：
echo.
echo 1. 打开浏览器访问：
echo    https://github.com/ossrs/srs/releases
echo.
echo 2. 找到最新版本（比如 v6.x.x）
echo.
echo 3. 下载 SRS-Windows-x86_64-xxx.zip
echo.
echo 4. 解压到当前目录 (d:\大三\大三上\Web\FastApi\rtmp-server)
echo.
echo 5. 运行解压后的: objs\srs.exe
echo.
echo ============================================================
echo 或者使用更简单的方法：安装Docker Desktop
echo ============================================================
echo.
echo 下载Docker Desktop:
echo https://www.docker.com/products/docker-desktop
echo.
echo 安装后执行命令：
echo docker run -d -p 1935:1935 -p 8080:8080 ossrs/srs:5
echo.
pause
