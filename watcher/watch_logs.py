import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ==========================================
# MINI SIEM LOG WATCHER
# ==========================================

LOG_FOLDER = "logs"
LOG_FILE = "sample.log"


class LogHandler(FileSystemEventHandler):

    def on_modified(self, event):

        # Ignore directories
        if event.is_directory:
            return

        # Watch only sample.log
        if event.src_path.endswith(LOG_FILE):

            print("\n" + "=" * 60)
            print(" NEW LOG DETECTED")
            print("=" * 60)

            try:
                print("Running Smart Collector...")
                subprocess.run(["python", "collector.py"], check=True)

                print("\nRunning Analyzer...")
                subprocess.run(["python", "analyzer.py"], check=True)

                print("\nMini SIEM Updated Successfully!")

            except subprocess.CalledProcessError as error:
                print("\nError while executing:", error)

            print("=" * 60)


# ==========================================
# Main Program
# ==========================================

if __name__ == "__main__":

    event_handler = LogHandler()

    observer = Observer()

    observer.schedule(
        event_handler,
        path=LOG_FOLDER,
        recursive=False
    )

    observer.start()

    print("=" * 60)
    print("      MINI SIEM REAL-TIME LOG WATCHER")
    print("=" * 60)
    print("Monitoring : logs/sample.log")
    print("Collector  : Enabled")
    print("Analyzer   : Enabled")
    print("Status     : Running")
    print("Press CTRL + C to stop")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping Mini SIEM Watcher...")
        observer.stop()

    observer.join()

    print("Watcher Stopped Successfully.")