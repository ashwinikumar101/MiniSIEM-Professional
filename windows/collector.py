# ==========================================
# MiniSIEM
# Windows Smart Event Collector
# Version 2.0
# ==========================================

import time
import win32evtlog

from parser import parse_event
from event_ids import EVENT_IDS
from database import save_log
from state import load_last_record, save_last_record

LOG_NAME = "Security"
POLL_INTERVAL = 5
MAX_EVENTS = 50


def collect_events():

    print("=" * 70)
    print(" MiniSIEM Windows Smart Collector")
    print("=" * 70)

    print("Status      : RUNNING")
    print("Watching    :", LOG_NAME)
    print("Interval    :", POLL_INTERVAL, "Seconds")
    print("=" * 70)

    last_record = load_last_record()

    print(f"Last Record : {last_record}\n")

    try:

        while True:

            newest_record = last_record

            handle = win32evtlog.EvtQuery(
                LOG_NAME,
                win32evtlog.EvtQueryReverseDirection,
                "*"
            )

            events = win32evtlog.EvtNext(handle, MAX_EVENTS)

            if events:

                # Process oldest first
                events.reverse()

                for event in events:

                    xml = win32evtlog.EvtRender(
                        event,
                        win32evtlog.EvtRenderEventXml
                    )

                    data = parse_event(xml)

                    record_id = data["record_id"]

                    # Skip events already processed
                    if record_id <= last_record:
                        continue

                    if record_id > newest_record:
                        newest_record = record_id

                    event_id = data["event_id"]

                    # Ignore unsupported events
                    if event_id not in EVENT_IDS:
                        continue

                    event_name = EVENT_IDS[event_id]

                    timestamp = data["timestamp"]

                    username = (
                        data["username"]
                        if data["username"]
                        else "Unknown"
                    )

                    ip = (
                        data["ip"]
                        if data["ip"] not in ("", "-")
                        else "Local"
                    )

                    domain = data["domain"] or "-"
                    workstation = data["workstation"] or "-"
                    process = data["process"] or "-"
                    logon_type = data["logon_type"] or "-"
                    authentication = data["authentication"] or "-"

                    inserted = save_log(
                        timestamp,
                        event_name,
                        username,
                        ip
                    )

                    if inserted:

                        print("-" * 70)
                        print("NEW EVENT DETECTED")
                        print("-" * 70)
                        print(f"Record ID      : {record_id}")
                        print(f"Event ID       : {event_id}")
                        print(f"Event Name     : {event_name}")
                        print(f"Username       : {username}")
                        print(f"Domain         : {domain}")
                        print(f"Computer       : {data['computer']}")
                        print(f"Workstation    : {workstation}")
                        print(f"Source IP      : {ip}")
                        print(f"Logon Type     : {logon_type}")
                        print(f"Authentication : {authentication}")
                        print(f"Process        : {process}")
                        print(f"Time           : {timestamp}")
                        print("Saved          : YES")
                        print()

            # Save newest processed record
            if newest_record > last_record:

                save_last_record(newest_record)
                last_record = newest_record

            print(f"Waiting {POLL_INTERVAL} seconds...\n")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:

        print("\n")
        print("=" * 70)
        print("MiniSIEM Collector Stopped")
        print("=" * 70)

    except Exception as e:

        print("\nCollector Error")
        print(e)


if __name__ == "__main__":

    collect_events()