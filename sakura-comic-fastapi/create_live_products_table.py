"""
创建直播带货商品表
"""
import asyncio
from sqlalchemy import text
from app.config import AsyncSessionLocal

async def create_products_table():
    """创建直播商品表"""
    async with AsyncSessionLocal() as db:
        try:
            # 创建直播商品表
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS live_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    product_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    original_price DECIMAL(10, 2),
                    stock INTEGER DEFAULT 0,
                    product_image VARCHAR(500),
                    purchase_link VARCHAR(500),
                    is_active BOOLEAN DEFAULT 1,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES live_rooms(id)
                )
            """)
            
            await db.execute(create_table_sql)
            await db.commit()
            
            print("直播商品表创建成功！")
            
            # 添加测试数据
            test_data_sql = text("""
                INSERT INTO live_products 
                (room_id, product_name, description, price, original_price, stock, product_image, purchase_link, sort_order)
                VALUES 
                (1, '限时优惠套装', '超值组合，买一送一', 199.00, 399.00, 100, 
                 'https://via.placeholder.com/300x300?text=Product1', 
                 'https://example.com/product1', 1),
                (1, '热销爆款商品', '网红推荐，质量保证', 99.00, 149.00, 50,
                 'https://via.placeholder.com/300x300?text=Product2',
                 'https://example.com/product2', 2),
                (1, '新品首发特惠', '限量发售，先到先得', 299.00, 499.00, 30,
                 'https://via.placeholder.com/300x300?text=Product3',
                 'https://example.com/product3', 3)
            """)
            
            await db.execute(test_data_sql)
            await db.commit()
            
            print("测试商品数据添加成功！")
            
            # 验证
            result = await db.execute(text("SELECT * FROM live_products"))
            products = result.fetchall()
            print(f"\n当前商品总数: {len(products)}")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_products_table())
