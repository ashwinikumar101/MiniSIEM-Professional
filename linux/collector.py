"""
=========================================================
MiniSIEM Professional Edition
Linux Log Collector
Author  : Ashwini
Version : 2.0
=========================================================
"""

import os
import time
import sqlite3
import platform
from datetime import datetime

# Import Linux Parser
from parser import parse_log_line

# =========================================================
# Database
# =========================================================

DATABASE = "database/siem.db"

# =========================================================
# Linux Authentication Log Locations
# =========================================================

LOG_FILES = {
    "Ubuntu": "/var/log/auth.log",
    "Debian": "/var/log/auth.log",
    "Kali": "/var/log/auth.log",
    "RedHat": "/var/log/secure",
    "Rocky": "/var/log/secure",
    "CentOS": "/var/log/secure"
}

# =========================================================
# Detect Linux Distribution
# =========================================================

def detect_distribution():

    if os.path.exists("/etc/os-release"):

        with open("/etc/os-release", "r") as file:

            data = file.read().lower()

            if "ubuntu" in data:
                return "Ubuntu"

            elif "debian" in data:
                return "Debian"

            elif "kali" in data:
                return "Kali"

            elif "rocky" in data:
                return "Rocky"

            elif "centos" in data:
                return "CentOS"

            elif "rhel" in data:
                return "RedHat"

    return platform.system()

# =========================================================
# Get Linux Authentication Log
# =========================================================

def get_log_file():

    distro = detect_distribution()

    return LOG_FILES.get(distro)

# =========================================================
# Database Connection
# =========================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    return conn

# =========================================================
# Save Event
# =========================================================

def save_event(event):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO logs
        (
            timestamp,
            event,
            username,
            ip
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            event["timestamp"],
            event["event"],
            event["username"],
            event["ip"]
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# Read Linux Authentication Log
# =========================================================

def collect_logs():

    logfile = get_log_file()

    if logfile is None:

        print("Linux authentication log not found.")

        return

    if not os.path.exists(logfile):

        print("Log file does not exist.")

        return

    print("=" * 60)
    print("MiniSIEM Linux Collector Started")
    print("=" * 60)

    print("Distribution :", detect_distribution())
    print("Monitoring :", logfile)
    print()

    with open(logfile, "r") as file:

        file.seek(0, os.SEEK_END)

        while True:

            line = file.readline()

            if not line:

                time.sleep(1)

                continue

            event = parse_log_line(line)

            if event:

                save_event(event)

                print(event)

# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    collect_logs()