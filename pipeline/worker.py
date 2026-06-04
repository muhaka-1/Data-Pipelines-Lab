import argparse
import os
import time

from db import (
    fetch_new_events,
    insert_reading,
    mark_duplicate,
    mark_processed,
    move_to_dead_letter,
    reading_exists,
)
from validation import validate_payload


def process_event(raw_event):
    payload = raw_event["payload"]

    # TODO Övning 2: Log event id before processing
    print(f"PROCESSING raw_event_id={raw_event['id']} event_id={raw_event.get('event_id')}")

    reading, error = validate_payload(payload)
    if error is not None:
        # TODO Övning 2: Improved error message with field and value context
        print(f"FAILED raw_event_id={raw_event['id']} error={error}")
        move_to_dead_letter(raw_event, error)
        return

    if reading_exists(reading["event_id"]):
        message = f"Duplicate eventId: {reading['event_id']}"
        print(f"DUPLICATE raw_event_id={raw_event['id']} event_id={reading['event_id']}")
        # TODO Övning 2: Duplicates stay in raw_events as 'duplicate', not in dead_letter
        mark_duplicate(raw_event["id"], message)
        return

    # TODO Extra: Temperature warning
    if reading["temperature"] > 28:
        print(f"VARNING hög temperatur: {reading['temperature']}°C device={reading['device_id']}")

    insert_reading(reading)
    mark_processed(raw_event["id"])
    print(
        f"PROCESSED raw_event_id={raw_event['id']} "
        f"event_id={reading['event_id']} "
        f"device_id={reading['device_id']}"
    )


def run_once():
    # TODO Extra: Track counts per outcome
    events = fetch_new_events()

    if not events:
        print("No new events")
        return {"processed": 0, "failed": 0, "duplicate": 0, "total": 0}

    counts = {"processed": 0, "failed": 0, "duplicate": 0, "total": len(events)}

    for raw_event in events:
        process_event(raw_event)

    print(f"BATCH DONE total={counts['total']}")
    return counts


def run_forever():
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))

    # TODO Extra: Read BATCH_SIZE from environment
    batch_size = int(os.getenv("BATCH_SIZE", "10"))
    print(f"Pipeline worker started. Poll interval: {poll_interval}s, batch size: {batch_size}")

    while True:
        run_once()
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Process one batch and exit")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_forever()


if __name__ == "__main__":
    main()