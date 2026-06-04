from datetime import datetime

REQUIRED_FIELDS = ["eventId", "deviceId", "humidity", "timestamp"]
# Note: "temperature" removed from required — handled separately below
# to support both "temperature" and "temp" (firmware-incident compatibility)


def validate_payload(payload):
    if not isinstance(payload, dict):
        return None, "Payload måste vara ett JSON-objekt"

    # TODO Övning 2: Accept both "temperature" and "temp"
    if "temperature" in payload:
        temperature_value = payload["temperature"]
    elif "temp" in payload:
        temperature_value = payload["temp"]
    else:
        return None, "Missing required field: temperature (or temp)"

    for field in REQUIRED_FIELDS:
        if field not in payload:
            return None, f"Missing required field: {field}"

    if not isinstance(payload["eventId"], str) or payload["eventId"].strip() == "":
        return None, "eventId must be a non-empty string"

    if not isinstance(payload["deviceId"], str) or payload["deviceId"].strip() == "":
        return None, "deviceId måste vara en text som inte är tom"

    try:
        temperature = float(temperature_value)
    except (TypeError, ValueError):
        return None, f"temperature must be a number, got: {temperature_value!r}"

    # TODO Övning 2: Sanity check for temperature
    if temperature < -40 or temperature > 80:
        return None, f"temperature out of range: {temperature} (expected -40 to 80)"

    try:
        humidity = float(payload["humidity"])
    except (TypeError, ValueError):
        return None, f"humidity must be a number, got: {payload['humidity']!r}"

    if humidity < 0 or humidity > 100:
        return None, "humidity must be between 0 and 100"

    measured_at = parse_timestamp(payload["timestamp"])
    if measured_at is None:
        return None, f"timestamp must be ISO format, got: {payload['timestamp']!r}"

    reading = {
        "event_id": payload["eventId"],
        "device_id": payload["deviceId"],
        "temperature": temperature,
        "humidity": humidity,
        "measured_at": measured_at,
    }

    return reading, None


def parse_timestamp(value):
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None