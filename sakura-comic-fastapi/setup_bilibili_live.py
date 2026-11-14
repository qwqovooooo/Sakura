"""
直接配置B站直播的脚本
"""
import asyncio
from sqlalchemy import text
from app.config import AsyncSessionLocal

async def setup_bilibili_live():
    """配置OBS推流 - 使用本地模拟配置"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(text("SELECT id FROM live_rooms"))
            rooms = result.fetchall()
            
            if not rooms:
                print("没有找到直播间，请先在网页上创建直播间")
                return
            
            room_id = rooms[0][0]
            
            # 生成OBS配置
            stream_key = f"room_{room_id}"
            rtmp_url = "rtmp://localhost/live"
            flv_url = f"http://localhost:8080/live/{stream_key}.flv"
            
            update_sql = text("""
                UPDATE live_rooms 
                SET source_type = 'self',
                    source_url = NULL,
                    rtmp_url = :rtmp_url,
                    stream_key = :stream_key,
                    flv_url = :flv_url,
                    title = 'OBS直播测试',
                    is_live = 0,
                    status = 'offline'
                WHERE id = :room_id
            """)
            
            await db.execute(update_sql, {
                "room_id": room_id,
                "rtmp_url": rtmp_url,
                "stream_key": stream_key,
                "flv_url": flv_url
            })
            await db.commit()
            
            print("\n" + "="*60)
            print("OBS Studio 配置信息")
            print("="*60)
            print(f"\nRTMP服务器: {rtmp_url}")
            print(f"串流密钥: {stream_key}")
            print(f"播放地址: {flv_url}")
            
            print("\n" + "="*60)
            print("重要：需要先启动RTMP服务器")
            print("="*60)
            
            print("\n最简单的方法：下载并解压SRS")
            print("\n1. 下载SRS Windows版：")
            print("   https://github.com/ossrs/srs/releases")
            print("   找到最新版本，下载 SRS-Windows-x86_64-xxx.zip")
            
            print("\n2. 解压后运行：")
            print("   ./objs/srs.exe -c conf/rtmp.conf")
            
            print("\n或者使用Docker（如果你愿意安装）：")
            print("   docker run -d -p 1935:1935 -p 8080:8080 ossrs/srs:5")
            
            print("\n" + "="*60)
            print("服务器启动后，配置OBS Studio")
            print("="*60)
            print("\n1. 打开OBS Studio")
            print("2. 点击 '设置' 按钮")
            print("3. 选择 '推流' 选项卡")
            print("4. 服务：选择 '自定义'")
            print(f"5. 服务器：{rtmp_url}")
            print(f"6. 串流密钥：{stream_key}")
            print("7. 点击 '确定'")
            print("8. 添加场景和来源（比如显示器捕获）")
            print("9. 点击 '开始推流'")
            
            print("\n" + "="*60)
            print("网页端操作")
            print("="*60)
            print("\n1. 刷新浏览器页面（Ctrl+F5）")
            print("2. 进入 '我的直播间'")
            print("3. 点击 '开始直播'")
            print("4. 点击 '查看直播间'")
            print("5. 等待几秒后即可看到直播画面")
            
            print("\n" + "="*60)
            print("✓ 配置完成！")
            print("="*60)
            
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_bilibili_live())
