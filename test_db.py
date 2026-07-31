from db import get_connection

conn = get_connection()

print("✅ Database connection established!")

conn.close()