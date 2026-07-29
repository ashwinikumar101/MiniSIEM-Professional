# ==========================================
# MiniSIEM Agent
# Metrics Engine
# ==========================================

import time


class Metrics:

    def __init__(self):

        self.start_time = time.time()

        self.events = 0

        self.duplicates = 0

        self.errors = 0

    def event(self):

        self.events += 1

    def duplicate(self):

        self.duplicates += 1

    def error(self):

        self.errors += 1

    def uptime(self):

        return int(time.time() - self.start_time)

    def status(self):

        return {

            "uptime": self.uptime(),

            "events": self.events,

            "duplicates": self.duplicates,

            "errors": self.errors

        }


metrics = Metrics()