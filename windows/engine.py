# ==========================================
# MiniSIEM
# Collector Engine
# Version 2.0
# ==========================================

import time

from collector import collect_events


class CollectorEngine:

    def __init__(self):

        self.running = False

        self.start_time = None

        self.events = 0

    def start(self):

        if self.running:

            print("Collector is already running.")
            return

        self.running = True

        self.start_time = time.time()

        print("=" * 60)
        print(" MiniSIEM Collector Engine Started")
        print("=" * 60)

        self.monitor()

    def monitor(self):

        while self.running:

            try:

                collect_events()

            except Exception as e:

                print("Collector Error:", e)

            time.sleep(5)

    def stop(self):

        self.running = False

        print("\nCollector Stopped")

    def status(self):

        uptime = 0

        if self.start_time:

            uptime = int(time.time() - self.start_time)

        return {

            "running": self.running,

            "uptime": uptime,

            "events": self.events

        }


engine = CollectorEngine()


if __name__ == "__main__":

    try:

        engine.start()

    except KeyboardInterrupt:

        engine.stop()