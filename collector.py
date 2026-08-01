"""
=========================================================
MiniSIEM Professional Edition
Windows Smart Log Collector
Author  : Ashwini
Version : 2.0
=========================================================
"""

from db import get_connection
import psycopg2.extras
import os
import socket

# =========================================================
# Configuration
# =========================================================

LOG_FILE = "logs/sample.log"
POSITION_FILE = "logs/last_position.txt"

# =========================================================
# Get Hostname
# =========================================================

HOSTNAME = socket.gethostname()

# =========================================================
# Database Connection
# =========================================================

conn = get_connection()

cursor = conn.cursor(
    cursor_factory=psycopg2.extras.RealDictCursor
)

# =========================================================
# Create Position File
# =========================================================

if not os.path.exists(POSITION_FILE):

    with open(POSITION_FILE, "w") as file:

        file.write("0")

# =========================================================
# Read Last Position
# =========================================================

with open(POSITION_FILE, "r") as file:

    last_position = int(file.read())

# =========================================================
# Open Log File
# =========================================================

with open(LOG_FILE, "r") as logfile:

    logfile.seek(last_position)

    imported_logs = 0

    skipped_logs = 0

    # =====================================================
    # Read New Log Entries
    # =====================================================

    for line in logfile:

        line = line.strip()

        if not line:

            continue

        try:

            parts = line.split()

            timestamp = parts[0] + " " + parts[1]

            event = parts[2]

            username = parts[3].split("=")[1]

            ip = parts[4].split("=")[1]

            # =================================================
            # Event Severity
            # =================================================

            if event == "LOGIN_SUCCESS":

                severity = "LOW"

            elif event == "LOGIN_FAILED":

                severity = "MEDIUM"

            elif event == "BRUTE_FORCE":

                severity = "HIGH"

            elif event == "ACCOUNT_LOCKED":

                severity = "HIGH"

            else:

                severity = "LOW"

            # =================================================
            # Duplicate Check
            # =================================================

            cursor.execute("""

                SELECT COUNT(*)

                FROM logs

                WHERE

                    timestamp=%s

                    AND event=%s

                    AND username=%s

                    AND ip=%s

            """, (

                timestamp,

                event,

                username,

                ip

            ))

            exists = cursor.fetchone()["count"]

            if exists:

                skipped_logs += 1

                continue

            # =================================================
            # Insert Log
            # =================================================

            cursor.execute("""

                INSERT INTO logs
                (

                    timestamp,

                    event,

                    username,

                    ip,

                    source,

                    hostname,

                    severity

                )

                VALUES (%s, %s, %s, %s, %s, %s, %s)

            """, (

                timestamp,

                event,

                username,

                ip,

                "Windows",

                HOSTNAME,

                severity

            ))

            imported_logs += 1

        except Exception as error:

            print("Skipped Invalid Log :", line)

            print(error)    

    # =====================================================
    # Save Current Position
    # =====================================================

    current_position = logfile.tell()

# =========================================================
# Save Position
# =========================================================

with open(POSITION_FILE, "w") as file:

    file.write(str(current_position))

# =========================================================
# Commit Changes
# =========================================================

conn.commit()

conn.close()

# =========================================================
# Status
# =========================================================

print("=" * 60)
print("MiniSIEM Professional Collector")
print("=" * 60)

print("Hostname            :", HOSTNAME)
print("Source              : Windows")
print("Imported Logs       :", imported_logs)
print("Duplicate Logs      :", skipped_logs)
print("Database Updated    : Yes")

print("=" * 60)