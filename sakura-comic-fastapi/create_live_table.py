"""
创建直播间表
"""
import sqlite3
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "sakura.db"

def create_live_room_table():
    """创建直播间表"""
    print("=" * 50)
    print("创建直播间表")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 创建直播间表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS live_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                
                user_id INTEGER NOT NULL,
                anchor_name VARCHAR(50),
                
                status VARCHAR(20) DEFAULT 'offline',
                is_live BOOLEAN DEFAULT 0,
                
                stream_key VARCHAR(100) UNIQUE NOT NULL,
                rtmp_url VARCHAR(200),
                hls_url VARCHAR(200),
                flv_url VARCHAR(200),
                
                viewer_count INTEGER DEFAULT 0,
                total_viewers INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                
                cover_image VARCHAR(500),
                category VARCHAR(50),
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                ended_at DATETIME
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_live_rooms_user_id 
            ON live_rooms(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_live_rooms_is_live 
            ON live_rooms(is_live)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_live_rooms_category 
            ON live_rooms(category)
        """)
        
        conn.commit()
        print("\n✅ 直播间表创建成功！")
        
        # 查看表结构
        cursor.execute("PRAGMA table_info(live_rooms)")
        columns = cursor.fetchall()
        
        print("\n表结构:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
    except Exception as e:
        print(f"\n❌ 创建表失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_live_room_table()
