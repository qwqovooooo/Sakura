import sqlite3

conn = sqlite3.connect('sakura.db')
cursor = conn.cursor()

# 先查看表结构
cursor.execute("PRAGMA table_info(live_rooms)")
print('\n表结构:')
for row in cursor.fetchall():
    print(row)

print('\n\n直播间数据:')
cursor.execute('SELECT * FROM live_rooms')
for row in cursor.fetchall():
    print(row)

conn.close()
