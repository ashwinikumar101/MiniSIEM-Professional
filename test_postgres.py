from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL =", DATABASE_URL)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected to PostgreSQL successfully!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:")
    print(e)