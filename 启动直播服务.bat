@echo off
chcp 65001 >nul
echo ========================================
echo 启动直播服务
echo ========================================
echo.

echo [1/3] 检查并启动 SRS RTMP 服务器...
docker start srs 2>nul
if errorlevel 1 (
    echo SRS容器不存在，正在创建并启动...
    docker run -d -p 1935:1935 -p 8080:8080 --name srs ossrs/srs:5
) else (
    echo SRS服务器已启动
)
echo.

echo [2/3] 启动 FastAPI 后端服务...
cd /d "d:\大三\大三上\Web\FastApi\sakura-comic-fastapi"
start "FastAPI后端" cmd /k "call venv\Scripts\activate && python run.py"
timeout /t 3 /nobreak >nul
echo.

echo [3/3] 启动 Vue 前端服务...
cd /d "d:\大三\大三上\Web\FastApi\sakura-comic-vue-main"
start "Vue前端" cmd /k "npm run dev"
echo.

echo ========================================
echo 所有服务启动完成！
echo ========================================
echo.
echo 服务地址：
echo - 前端页面: http://localhost:5173
echo - 后端API: http://localhost:8000
echo - RTMP推流: rtmp://localhost/live
echo - 直播播放: http://localhost:8080/live/房间ID.flv
echo.
echo OBS推流设置：
echo - 服务器: rtmp://localhost/live
echo - 串流密钥: room_1 (或你的房间ID)
echo.
pause
