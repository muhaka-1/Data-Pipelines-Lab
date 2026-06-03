import os
import time

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5002")


EVENTS = [
    {
        "eventId": "evt-1001",
        "deviceId": "sensor-entrance-1",
        "temperature": 21.4,
        "humidity": 42,
        "timestamp": "2026-06-03T09:00:00Z",
    },
    {
        "eventId": "evt-1002",
        "deviceId": "sensor-classroom-2",
        "temperature": 23.1,
        "humidity": 46,
        "timestamp": "2026-06-03T09:05:00Z",
    },
    {
        "eventId": "evt-1003",
        "deviceId": "sensor-lab-1",
        "temperature": "warm",
        "humidity": 50,
        "timestamp": "2026-06-03T09:10:00Z",
    },
    {
        "eventId": "evt-1004",
        "deviceId": "sensor-lab-2",
        "temp": 22.0,
        "humidity": 44,
        "timestamp": "2026-06-03T09:15:00Z",
    },
    {
        "eventId": "evt-1005",
        "deviceId": "sensor-server-room",
        "temperature": 29.8,
        "humidity": -5,
        "timestamp": "2026-06-03T09:20:00Z",
    },
    {
        "eventId": "evt-1002",
        "deviceId": "sensor-classroom-2",
        "temperature": 23.1,
        "humidity": 46,
        "timestamp": "2026-06-03T09:05:00Z",
    },
]


def print_response(title, response):
    print("\n" + "=" * 60)
    print(title)
    print("Status:", response.status_code)

    try:
        print("JSON:", response.json())
    except Exception:
        print("Text:", response.text)


def main():
    health = requests.get(f"{API_BASE_URL}/health", timeout=10)
    print_response("GET /health", health)

    for event in EVENTS:
        response = requests.post(f"{API_BASE_URL}/events", json=event, timeout=10)
        print_response(f"POST /events {event.get('eventId')}", response)
        time.sleep(0.5)

    metrics = requests.get(f"{API_BASE_URL}/metrics", timeout=10)
    print_response("GET /metrics", metrics)

    events = requests.get(f"{API_BASE_URL}/events", timeout=10)
    print_response("GET /events", events)


if __name__ == "__main__":
    main()
