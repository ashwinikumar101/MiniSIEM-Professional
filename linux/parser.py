"""
=========================================================
MiniSIEM Professional Edition
Linux Log Parser
Author  : Ashwini
Version : 2.0
=========================================================
"""

import re
from datetime import datetime

# =========================================================
# Parse Linux Authentication Log
# =========================================================

def parse_log_line(line):

    line = line.strip()

    # Ignore empty lines
    if not line:
        return None

    # Current year
    current_year = datetime.now().year

    # =====================================================
    # Failed SSH Login
    # =====================================================

    failed = re.search(

        r"^(\w+\s+\d+\s+\d+:\d+:\d+).*Failed password for (invalid user )?(\S+) from ([\d\.]+)",

        line

    )

    if failed:

        timestamp = datetime.strptime(

            f"{current_year} {failed.group(1)}",

            "%Y %b %d %H:%M:%S"

        )

        return {

            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),

            "event": "SSH_LOGIN_FAILED",

            "username": failed.group(3),

            "ip": failed.group(4)

        }

    # =====================================================
    # Successful SSH Login
    # =====================================================

    success = re.search(

        r"^(\w+\s+\d+\s+\d+:\d+:\d+).*Accepted password for (\S+) from ([\d\.]+)",

        line

    )

    if success:

        timestamp = datetime.strptime(

            f"{current_year} {success.group(1)}",

            "%Y %b %d %H:%M:%S"

        )

        return {

            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),

            "event": "SSH_LOGIN_SUCCESS",

            "username": success.group(2),

            "ip": success.group(3)

        }

    # =====================================================
    # Root Login
    # =====================================================

    root = re.search(

        r"^(\w+\s+\d+\s+\d+:\d+:\d+).*session opened for user root",

        line

    )

    if root:

        timestamp = datetime.strptime(

            f"{current_year} {root.group(1)}",

            "%Y %b %d %H:%M:%S"

        )

        return {

            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),

            "event": "ROOT_LOGIN",

            "username": "root",

            "ip": "localhost"

        }

    # =====================================================
    # Sudo Command
    # =====================================================

    sudo = re.search(

        r"^(\w+\s+\d+\s+\d+:\d+:\d+).*sudo.*USER=root",

        line

    )

    if sudo:

        timestamp = datetime.strptime(

            f"{current_year} {sudo.group(1)}",

            "%Y %b %d %H:%M:%S"

        )

        return {

            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),

            "event": "SUDO_COMMAND",

            "username": "Unknown",

            "ip": "localhost"

        }

    return None


# =========================================================
# Test Parser
# =========================================================

if __name__ == "__main__":

    samples = [

        "Jul 28 10:15:23 kali sshd[1523]: Failed password for root from 192.168.1.100 port 53122 ssh2",

        "Jul 28 10:16:10 kali sshd[1523]: Accepted password for ashwini from 192.168.1.50 port 51122 ssh2",

        "Jul 28 10:20:00 kali sudo: pam_unix(sudo:session): session opened for user root",

        "Jul 28 10:30:00 kali sudo: USER=root ; COMMAND=/usr/bin/apt update"

    ]

    print("=" * 60)
    print("MiniSIEM Linux Parser Test")
    print("=" * 60)

    for sample in samples:

        print(parse_log_line(sample))