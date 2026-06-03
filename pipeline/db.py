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


def fetch_new_events(limit=10):
    query = """
        SELECT id, event_id, payload, received_at
        FROM raw_events
        WHERE status = 'new'
        ORDER BY id
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (limit,))
            return [dict(row) for row in cur.fetchall()]


def reading_exists(event_id):
    query = "SELECT EXISTS (SELECT 1 FROM readings WHERE event_id = %s);"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (event_id,))
            return cur.fetchone()[0]


def insert_reading(reading):
    query = """
        INSERT INTO readings (event_id, device_id, temperature, humidity, measured_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    reading["event_id"],
                    reading["device_id"],
                    reading["temperature"],
                    reading["humidity"],
                    reading["measured_at"],
                ),
            )


def mark_processed(raw_event_id):
    query = """
        UPDATE raw_events
        SET status = 'processed', processed_at = NOW()
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (raw_event_id,))


def mark_duplicate(raw_event_id, message):
    query = """
        UPDATE raw_events
        SET status = 'duplicate', error_message = %s, processed_at = NOW()
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (message, raw_event_id))


def move_to_dead_letter(raw_event, error_message):
    insert_query = """
        INSERT INTO dead_letter_events (raw_event_id, event_id, payload, error_message)
        VALUES (%s, %s, %s, %s);
    """

    update_query = """
        UPDATE raw_events
        SET status = 'failed', error_message = %s, processed_at = NOW()
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                insert_query,
                (
                    raw_event["id"],
                    raw_event.get("event_id"),
                    psycopg2.extras.Json(raw_event["payload"]),
                    error_message,
                ),
            )
            cur.execute(update_query, (error_message, raw_event["id"]))
