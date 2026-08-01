from db import get_connection
import psycopg2.extras

# ==========================================
# View Logs
# ==========================================

conn = get_connection()

cursor = conn.cursor(
    cursor_factory=psycopg2.extras.RealDictCursor
)

cursor.execute("""
SELECT *
FROM logs
ORDER BY id
""")

rows = cursor.fetchall()

for row in rows:

    print(row)

cursor.close()
conn.close()