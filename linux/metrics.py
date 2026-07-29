"""
=========================================================
MiniSIEM Professional Edition
Linux Metrics
Author  : Ashwini
Version : 2.0
=========================================================
"""

import time

# =========================================================
# Collector Start Time
# =========================================================

START_TIME = time.time()

# =========================================================
# Metrics
# =========================================================

EVENTS_PROCESSED = 0
DUPLICATES_SKIPPED = 0
ERRORS = 0
LAST_RECORD = 0


# =========================================================
# Increment Events
# =========================================================

def event_processed():

    global EVENTS_PROCESSED

    EVENTS_PROCESSED += 1


# =========================================================
# Increment Duplicate Counter
# =========================================================

def duplicate_skipped():

    global DUPLICATES_SKIPPED

    DUPLICATES_SKIPPED += 1


# =========================================================
# Increment Error Counter
# =========================================================

def error_occurred():

    global ERRORS

    ERRORS += 1


# =========================================================
# Update Last Record
# =========================================================

def update_last_record(record):

    global LAST_RECORD

    LAST_RECORD = record


# =========================================================
# Get Status
# =========================================================

def status():

    uptime = time.time() - START_TIME

    eps = 0

    if uptime > 0:

        eps = round(EVENTS_PROCESSED / uptime, 2)

    return {

        "uptime": round(uptime, 2),

        "events_processed": EVENTS_PROCESSED,

        "duplicates_skipped": DUPLICATES_SKIPPED,

        "errors": ERRORS,

        "last_record_id": LAST_RECORD,

        "events_per_second": eps

    }


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    event_processed()
    event_processed()
    duplicate_skipped()
    error_occurred()
    update_last_record(25)

    print(status())