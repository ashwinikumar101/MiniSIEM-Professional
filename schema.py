from db import get_connection
from datetime import datetime
import bcrypt

# ==========================================
# Database Connection
# ==========================================

conn = get_connection()
cursor = conn.cursor()

print("==========================================")
print(" MiniSIEM Schema Initialization")
print("==========================================")

# ==========================================
# Users Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id SERIAL PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role VARCHAR(50) NOT NULL,

    created_at TIMESTAMP NOT NULL

)
""")

print("✅ Users table ready")