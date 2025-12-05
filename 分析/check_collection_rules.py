import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('data_dev.sqlite')
cursor = conn.cursor()

# 检查表结构
print("collection_rules表结构：")
cursor.execute("PRAGMA table_info(collection_rules);")
columns = cursor.fetchall()
for column in columns:
    print(f"- {column[1]} ({column[2]})")

# 检查数据
print("\ncollection_rules表内容：")
cursor.execute("SELECT * FROM collection_rules;")
data = cursor.fetchall()
if not data:
    print("表中没有数据")
else:
    for row in data:
        print(f"- ID: {row[0]}, 站点名称: {row[1]}, URL: {row[2]}")

# 关闭连接
conn.close()