"""
=========================================================
MiniSIEM Professional Edition
Linux Security Analyzer
Author  : Ashwini
Version : 2.0
=========================================================
"""

import sqlite3

DATABASE = "database/siem.db"

# =========================================================
# Database Connection
# =========================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# Detect SSH Brute Force
# =========================================================

def detect_bruteforce():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            ip,

            COUNT(*) AS attempts

        FROM logs

        WHERE event='SSH_LOGIN_FAILED'

        GROUP BY ip

        HAVING attempts >= 5

    """)

    attackers = cursor.fetchall()

    for attacker in attackers:

        print("=" * 60)
        print("🚨 SSH BRUTE FORCE DETECTED")
        print("IP Address :", attacker["ip"])
        print("Attempts   :", attacker["attempts"])
        print("=" * 60)

    conn.close()


# =========================================================
# Detect Root Login
# =========================================================

def detect_root_login():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM logs

        WHERE event='ROOT_LOGIN'

        ORDER BY id DESC

        LIMIT 5

    """)

    results = cursor.fetchall()

    if results:

        print("=" * 60)
        print("⚠ Root Login Detected")
        print("=" * 60)

        for row in results:

            print(dict(row))

    conn.close()


# =========================================================
# Detect Suspicious Sudo Usage
# =========================================================

def detect_sudo():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM logs

        WHERE event='SUDO_COMMAND'

        ORDER BY id DESC

        LIMIT 5

    """)

    results = cursor.fetchall()

    if results:

        print("=" * 60)
        print("⚠ Sudo Activity Detected")
        print("=" * 60)

        for row in results:

            print(dict(row))

    conn.close()


# =========================================================
# Run Analyzer
# =========================================================

def analyze():

    detect_bruteforce()

    detect_root_login()

    detect_sudo()


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    analyze()