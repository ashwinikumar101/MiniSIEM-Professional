# ==========================================
# MiniSIEM
# Collector Health Monitor
# Version 1.0
# ==========================================

import sqlite3
import os
from datetime import datetime

DATABASE = "database/siem.db"
STATE_FILE = os.path.join("windows", "collector.state")


class HealthMonitor:

    def __init__(self):

        self.last_scan = None

    # ----------------------------------
    # Check SQLite Database
    # ----------------------------------
    def database_status(self):

        try:

            conn = sqlite3.connect(DATABASE)
            conn.close()

            return "CONNECTED"

        except Exception:

            return "DISCONNECTED"

    # ----------------------------------
    # Check State File
    # ----------------------------------
    def state_status(self):

        if os.path.exists(STATE_FILE):

            return "OK"

        return "NOT FOUND"

    # ----------------------------------
    # Update Last Scan
    # ----------------------------------
    def update_scan(self):

        self.last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ----------------------------------
    # Get Health Status
    # ----------------------------------
    def status(self):

        database = self.database_status()

        state = self.state_status()

        overall = "HEALTHY"

        if database != "CONNECTED":

            overall = "WARNING"

        return {

            "collector": "RUNNING",

            "database": database,

            "state_file": state,

            "last_scan": self.last_scan,

            "overall": overall

        }


health = HealthMonitor()