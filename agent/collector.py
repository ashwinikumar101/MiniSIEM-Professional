# ==========================================
# MiniSIEM Agent
# Collector Engine
# Version 2.0
# ==========================================

import threading

from windows.collector import collect_events

from metrics import metrics


class CollectorEngine:

    def __init__(self):

        self.running = False

        self.threads = []

    def start_windows(self):

        print("Starting Windows Collector...")

        thread = threading.Thread(

            target=collect_events,

            daemon=True

        )

        thread.start()

        self.threads.append(thread)

    def start(self):

        if self.running:

            print("Collector already running.")

            return

        self.running = True

        print("=" * 60)
        print("MiniSIEM Agent Started")
        print("=" * 60)

        self.start_windows()

    def stop(self):

        print("\nStopping Agent...")

        self.running = False

    def status(self):

        return {

            "running": self.running,

            "threads": len(self.threads),

            "metrics": metrics.status()

        }


engine = CollectorEngine()


if __name__ == "__main__":

    engine.start()

    try:

        while True:
            pass

    except KeyboardInterrupt:

        engine.stop()

        print("MiniSIEM Agent Stopped")