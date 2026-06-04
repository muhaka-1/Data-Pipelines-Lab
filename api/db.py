import json
import os

import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        dbname=os.getenv("DB_NAME", "datapipeline"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )


def _convert_row(row):
    if row is None:
        return None

    item = dict(row)

    for field in ["received_at", "processed_at", "created_at", "measured_at", "failed_at"]:
        if item.get(field) is not None:
            item[field] = item[field].isoformat()

    if item.get("payload") is not None and isinstance(item["payload"], str):
        item["payload"] = json.loads(item["payload"])

    for field in ["temperature", "humidity"]:
        if item.get(field) is not None:
            item[field] = float(item[field])

    return item


def insert_raw_event(payload):
    query = """
        INSERT INTO raw_events (event_id, payload)
        VALUES (%s, %s)
        RETURNING id, event_id, payload, status, received_at, processed_at;
    """

    event_id = payload.get("eventId") if isinstance(payload, dict) else None

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (event_id, psycopg2.extras.Json(payload)))
            row = cur.fetchone()

    return _convert_row(row)


def list_raw_events(limit=20):
    # Extra Övning 1: clamp limit between 1 and 100
    if limit is None:
        limit = 20
    limit = max(1, min(int(limit), 100))

    query = """
        SELECT id, event_id, payload, status, error_message, received_at, processed_at
        FROM raw_events
        ORDER BY id DESC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [_convert_row(row) for row in rows]


def get_metrics():
    query = """
        SELECT
          COUNT(*) FILTER (WHERE status = 'new')        AS new_events,
          COUNT(*) FILTER (WHERE status = 'processed')  AS processed_events,
          COUNT(*) FILTER (WHERE status = 'failed')     AS failed_events,
          COUNT(*) FILTER (WHERE status = 'duplicate')  AS duplicate_events,
          MAX(received_at)                               AS latest_received_at,
          MAX(processed_at)                              AS latest_processed_at
        FROM raw_events;
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            raw_metrics = dict(cur.fetchone())

            # Convert timestamps to ISO strings
            for field in ["latest_received_at", "latest_processed_at"]:
                if raw_metrics.get(field) is not None:
                    raw_metrics[field] = raw_metrics[field].isoformat()

            cur.execute("SELECT COUNT(*) AS readings FROM readings;")
            readings = dict(cur.fetchone())

            cur.execute("SELECT COUNT(*) AS dead_letters FROM dead_letter_events;")
            dead_letters = dict(cur.fetchone())

            # TODO Övning 2: events per device
            cur.execute("""
                SELECT payload->>'deviceId' AS device_id, COUNT(*) AS events
                FROM raw_events
                GROUP BY device_id
                ORDER BY events DESC;
            """)
            events_per_device = [
                {"device_id": row["device_id"], "events": row["events"]}
                for row in cur.fetchall()
            ]

    total = raw_metrics.get("processed_events", 0) + raw_metrics.get("failed_events", 0)
    failed = raw_metrics.get("failed_events", 0)
    failed_pct = round((failed / total * 100), 1) if total > 0 else 0.0

    return {
        **raw_metrics,
        **readings,
        **dead_letters,
        "failed_percent": failed_pct,
        "events_per_device": events_per_device,
    }