# ==========================================
# MiniSIEM
# Collector Metrics Engine
# Version 1.0
# ==========================================

import time


class CollectorMetrics:

    def __init__(self):

        self.start_time = time.time()

        self.events_processed = 0

        self.duplicates_skipped = 0

        self.errors = 0

        self.last_record_id = 0

    # -----------------------------
    # Events Processed
    # -----------------------------
    def event_processed(self):

        self.events_processed += 1

    # -----------------------------
    # Duplicate Events
    # -----------------------------
    def duplicate(self):

        self.duplicates_skipped += 1

    # -----------------------------
    # Collector Errors
    # -----------------------------
    def error(self):

        self.errors += 1

    # -----------------------------
    # Update Last Record ID
    # -----------------------------
    def update_record(self, record_id):

        self.last_record_id = record_id

    # -----------------------------
    # Uptime
    # -----------------------------
    def uptime(self):

        seconds = int(time.time() - self.start_time)

        hours = seconds // 3600

        minutes = (seconds % 3600) // 60

        seconds = seconds % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # -----------------------------
    # Events Per Second
    # -----------------------------
    def events_per_second(self):

        elapsed = time.time() - self.start_time

        if elapsed <= 0:
            return 0

        return round(self.events_processed / elapsed, 2)

    # -----------------------------
    # Collector Status
    # -----------------------------
    def status(self):

        return {

            "uptime": self.uptime(),

            "events_processed": self.events_processed,

            "duplicates_skipped": self.duplicates_skipped,

            "errors": self.errors,

            "last_record_id": self.last_record_id,

            "events_per_second": self.events_per_second()

        }


metrics = CollectorMetrics()