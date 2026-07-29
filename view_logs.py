import sqlite3

conn = sqlite3.connect("database/siem.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM logs")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()