# ==========================================
# MiniSIEM
# Collector State Manager
# Version 2.0
# ==========================================

import os

# ------------------------------------------
# State File
# ------------------------------------------

STATE_FILE = os.path.join("windows", "collector.state")


# ------------------------------------------
# Load Last Processed Event Record ID
# ------------------------------------------

def load_last_record():

    try:

        # State file doesn't exist yet
        if not os.path.exists(STATE_FILE):
            return 0

        with open(STATE_FILE, "r", encoding="utf-8") as file:

            value = file.read().strip()

            if value == "":
                return 0

            return int(value)

    except (ValueError, OSError):

        # Corrupted or unreadable file
        return 0


# ------------------------------------------
# Save Last Processed Event Record ID
# ------------------------------------------

def save_last_record(record_id):

    try:

        # Ensure the windows folder exists
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

        with open(STATE_FILE, "w", encoding="utf-8") as file:

            file.write(str(record_id))

    except OSError as e:

        print(f"[STATE ERROR] Unable to save collector state: {e}")


# ------------------------------------------
# Reset Collector State
# ------------------------------------------

def reset_state():

    save_last_record(0)