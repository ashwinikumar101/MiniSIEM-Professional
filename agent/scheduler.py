# ==========================================
# MiniSIEM Agent
# Scheduler
# ==========================================

import time

from config import POLL_INTERVAL


def wait():

    time.sleep(POLL_INTERVAL)