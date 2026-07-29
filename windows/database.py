# ==========================================
# MiniSIEM
# Windows Database Functions
# Stage 2
# ==========================================

import sqlite3

DATABASE = "database/siem.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)
    return conn


# ==========================================
# Check Duplicate Log
# ==========================================
def log_exists(timestamp, event, username, ip):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM logs
        WHERE timestamp = ?
        AND event = ?
        AND username = ?
        AND ip = ?
        LIMIT 1
    """, (

        timestamp,
        event,
        username,
        ip

    ))

    result = cursor.fetchone()

    conn.close()

    return result is not None


# ==========================================
# Save Log
# ==========================================
def save_log(timestamp, event, username, ip):

    # Prevent duplicate records
    if log_exists(timestamp, event, username, ip):
        return False

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs
        (
            timestamp,
            event,
            username,
            ip
        )
        VALUES (?, ?, ?, ?)
    """, (

        timestamp,
        event,
        username,
        ip

    ))

    conn.commit()

    conn.close()

    return True