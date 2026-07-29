import sqlite3
from datetime import datetime
import bcrypt

# ==========================================
# MiniSIEM Database Initialization
# ==========================================

DATABASE = "database/siem.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# ==========================================
# Logs Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT NOT NULL,

    event TEXT NOT NULL,

    username TEXT,

    ip TEXT

)
""")

# ==========================================
# Upgrade Logs Table (Database Migration)
# ==========================================

# Add source column
try:
    cursor.execute("""
        ALTER TABLE logs
        ADD COLUMN source TEXT DEFAULT 'Windows'
    """)
    print("✅ Added column: source")
except sqlite3.OperationalError:
    print("ℹ️ Column already exists: source")

# Add hostname column
try:
    cursor.execute("""
        ALTER TABLE logs
        ADD COLUMN hostname TEXT DEFAULT 'Unknown'
    """)
    print("✅ Added column: hostname")
except sqlite3.OperationalError:
    print("ℹ️ Column already exists: hostname")

# Add severity column
try:
    cursor.execute("""
        ALTER TABLE logs
        ADD COLUMN severity TEXT DEFAULT 'LOW'
    """)
    print("✅ Added column: severity")
except sqlite3.OperationalError:
    print("ℹ️ Column already exists: severity")

# ==========================================
# Alerts Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    alert_type TEXT NOT NULL,

    ip TEXT,

    failed_attempts INTEGER,

    severity TEXT,

    recommendation TEXT

)
""")

# ==========================================
# Users Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role TEXT NOT NULL,

    created_at TEXT NOT NULL

)
""")

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
        "SELECT id FROM users WHERE username=?",
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
        (
            username,
            password,
            role,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            hashed_password,
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    print(f"✅ Created user: {username} ({role})")

# ==========================================
# Save Changes
# ==========================================

conn.commit()

conn.close()

print()
print("==========================================")
print(" MiniSIEM Database Initialized")
print("==========================================")
print(f"Database : {DATABASE}")
print("Status   : READY")
print("==========================================")