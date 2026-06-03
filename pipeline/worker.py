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

    # TODO Övning 2:
    # Skriv ut raw_event["id"] och raw_event["event_id"] innan validering.
    # Fråga: varför är logs viktiga i en pipeline?

    reading, error = validate_payload(payload)
    if error is not None:
        print(f"FAILED raw_event_id={raw_event['id']} error={error}")

        # TODO Övning 2:
        # Förbättra felmeddelandet som skickas till dead-letter.
        # Kan ni få med vilket fält som är fel och vilket värde som skickades?
        move_to_dead_letter(raw_event, error)
        return

    if reading_exists(reading["event_id"]):
        message = f"Duplicate eventId: {reading['event_id']}"
        print(f"DUPLICATE raw_event_id={raw_event['id']} event_id={reading['event_id']}")

        # TODO Övning 2:
        # Fundera på om en duplicate ska räknas som fel eller som ett normalt retry.
        # Ska dubletter hamna i dead_letter_events eller bara få statusen duplicate?
        mark_duplicate(raw_event["id"], message)
        return

    # TODO Extra:
    # Lägg till en enkel temperaturvarning.
    # Exempel: om reading["temperature"] > 28, skriv ut "VARNING hög temperatur".

    insert_reading(reading)
    mark_processed(raw_event["id"])
    print(
        "PROCESSED "
        f"raw_event_id={raw_event['id']} "
        f"event_id={reading['event_id']} "
        f"device_id={reading['device_id']}"
    )


def run_once():
    events = fetch_new_events()

    if not events:
        print("No new events")
        return 0

    for raw_event in events:
        process_event(raw_event)

    # TODO Extra:
    # Returnera gärna mer information än bara antal events.
    # Exempel: antal processed, failed och duplicate.
    return len(events)


def run_forever():
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))

    # TODO Extra:
    # Läs in BATCH_SIZE från miljövariabler och använd den i fetch_new_events().
    # Då kan ni testa vad som händer när pipelinen bara hinner ta några events per körning.

    print(f"Pipeline worker started. Poll interval: {poll_interval}s")

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
