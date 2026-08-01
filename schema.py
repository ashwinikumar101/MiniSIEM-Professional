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

# ==========================================
# Logs Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (

    id SERIAL PRIMARY KEY,

    timestamp TIMESTAMP NOT NULL,

    event VARCHAR(255) NOT NULL,

    username VARCHAR(100),

    ip VARCHAR(50),

    source VARCHAR(100) DEFAULT 'Windows',

    hostname VARCHAR(255) DEFAULT 'Unknown',

    severity VARCHAR(20) DEFAULT 'LOW'

)
""")

print("✅ Logs table ready")

# ==========================================
# Alerts Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (

    id SERIAL PRIMARY KEY,

    alert_type VARCHAR(255) NOT NULL,

    ip VARCHAR(50),

    failed_attempts INTEGER,

    severity VARCHAR(20),

    recommendation TEXT

)
""")

print("✅ Alerts table ready")

# ==========================================
# Performance Indexes
# ==========================================

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_logs_timestamp
ON logs(timestamp)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_logs_event
ON logs(event)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_logs_ip
ON logs(ip)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_alerts_severity
ON alerts(severity)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_users_username
ON users(username)
""")

print("✅ Performance indexes ready")

# ==========================================
# Default Users
# ==========================================

default_users = [

    ("admin", "admin123", "Admin"),

    ("analyst", "analyst123", "Analyst"),

    ("viewer", "viewer123", "Viewer")

]

for username, password, role in default_users:

    cursor.execute(
        "SELECT id FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print(f"ℹ️ User already exists: {username}")
        continue

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO users
        (username, password, role, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (
            username,
            hashed_password,
            role,
            datetime.now()
        )
    )

    print(f"✅ Created user: {username}")

# ==========================================
# Save Changes
# ==========================================

conn.commit()
conn.close()

print("==========================================")
print(" PostgreSQL Schema Ready")
print("==========================================")