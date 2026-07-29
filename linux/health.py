"""
=========================================================
MiniSIEM Professional Edition
Linux Health Monitor
Author  : Ashwini
Version : 2.0
=========================================================
"""

import os
from datetime import datetime

# =========================================================
# Linux Authentication Log Locations
# =========================================================

LOG_FILES = [
    "/var/log/auth.log",
    "/var/log/secure"
]

# =========================================================
# Health Status
# =========================================================

def status():

    collector = "Stopped"
    database = "Unknown"
    logfile = "Not Found"
    overall = "Unhealthy"
    last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check Authentication Log
    for path in LOG_FILES:

        if os.path.exists(path):

            logfile = path
            collector = "Running"

            break

    # Database Status
    if os.path.exists("database/siem.db"):

        database = "Connected"

    # Overall Health
    if collector == "Running" and database == "Connected":

        overall = "Healthy"

    return {

        "collector": collector,

        "database": database,

        "log_file": logfile,

        "last_scan": last_scan,

        "overall": overall

    }


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MiniSIEM Linux Health")
    print("=" * 60)

    print(status())