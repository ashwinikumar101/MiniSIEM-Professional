"""
=========================================================
MiniSIEM Professional Edition
Linux Log Watcher
Author  : Ashwini
Version : 2.0
=========================================================
"""

import os
import time

from collector import collect_logs

# =========================================================
# Linux Authentication Log Files
# =========================================================

LOG_FILES = [

    "/var/log/auth.log",

    "/var/log/secure"

]

# =========================================================
# Find Existing Log File
# =========================================================

def get_log_file():

    for logfile in LOG_FILES:

        if os.path.exists(logfile):

            return logfile

    return None


# =========================================================
# Watch Linux Log File
# =========================================================

def watch():

    logfile = get_log_file()

    if logfile is None:

        print("=" * 60)
        print("MiniSIEM Linux Watcher")
        print("=" * 60)
        print("No Linux authentication log found.")
        return

    print("=" * 60)
    print("MiniSIEM Linux Watcher Started")
    print("=" * 60)

    print("Watching :", logfile)

    last_modified = os.path.getmtime(logfile)

    while True:

        current_modified = os.path.getmtime(logfile)

        if current_modified != last_modified:

            print("New log detected...")

            collect_logs()

            last_modified = current_modified

        time.sleep(2)


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    watch()