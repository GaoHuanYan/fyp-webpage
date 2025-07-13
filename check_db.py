import sqlite3

DB_PATH = 'stock_data.db'

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("SELECT * FROM stock_data;")
rows = cursor.fetchall()

if rows:
    print("表中的数据：")
    for row in rows:
        print(row)
else:
    print("stock_data 表中没有数据！")

connection.close()