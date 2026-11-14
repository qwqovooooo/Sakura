import sqlite3

conn = sqlite3.connect('sakura.db')
cursor = conn.cursor()

cursor.execute('SELECT id, name, is_admin FROM sakura_user WHERE is_admin = 1')
print('\n管理员用户:')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, 用户名: {row[1]}, 管理员: {row[2]}')

conn.close()
