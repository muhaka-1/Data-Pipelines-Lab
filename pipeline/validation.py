from datetime import datetime


REQUIRED_FIELDS = ["eventId", "deviceId", "temperature", "humidity", "timestamp"]


# TODO Övning 2:
# Firmware-incidenten byter fältet "temperature" till "temp".
# Fundera på om REQUIRED_FIELDS fortfarande ska kräva "temperature",
# eller om temperaturfältet ska hanteras separat i validate_payload().


def validate_payload(payload):
    """
    Övning 2:
    Bygg ut valideringen om ni vill.

    Krav i startversionen:
    - alla obligatoriska fält ska finnas
    - temperature och humidity ska vara nummer
    - humidity ska vara mellan 0 och 100
    - timestamp ska gå att tolka som ISO-tid
    """
    if not isinstance(payload, dict):
        return None, "Payload måste vara ett JSON-objekt"

    # TODO Övning 2:
    # Gör valideringen mer bakåtkompatibel:
    # - acceptera "temperature"
    # - acceptera "temp"
    # - om båda saknas: returnera ett tydligt fel
    #
    # Tips: skapa en variabel temperature_value innan REQUIRED_FIELDS-loopen.

    for field in REQUIRED_FIELDS:
        if field not in payload:
            return None, f"Missing required field: {field}"

    if not isinstance(payload["eventId"], str) or payload["eventId"].strip() == "":
        return None, "eventId must be a non-empty string"

    if not isinstance(payload["deviceId"], str) or payload["deviceId"].strip() == "":
        return None, "deviceId måste vara en text som inte är tom"

    try:
        temperature = float(payload["temperature"])
    except (TypeError, ValueError):
        return None, "temperature must be a number"

    # TODO Övning 2:
    # Lägg till rimlighetskontroll för temperature.
    # Exempel för smart byggnad:
    # - under -40 är troligen fel
    # - över 80 är troligen fel
    #
    # Fråga: ska ett extremt värde alltid stoppas,
    # eller kan det ibland vara ett viktigt larm?

    try:
        humidity = float(payload["humidity"])
    except (TypeError, ValueError):
        return None, "humidity must be a number"

    if humidity < 0 or humidity > 100:
        return None, "humidity must be between 0 and 100"

    # TODO Extra:
    # Lägg till en enkel avvikelsemarkering.
    # Exempel: om temperature > 28, skriv ut ett tydligt meddelande i workern.
    # Behöver det sparas i databasen, i metrics eller bara i logs?

    measured_at = parse_timestamp(payload["timestamp"])
    if measured_at is None:
        return None, "timestamp must be ISO format"

    reading = {
        "event_id": payload["eventId"],
        "device_id": payload["deviceId"],
        "temperature": temperature,
        "humidity": humidity,
        "measured_at": measured_at,
    }

    return reading, None


def parse_timestamp(value):
    # TODO Övning 2:
    # Testa olika tidsformat.
    # Vilka format accepterar datetime.fromisoformat?
    # Vilka format borde pipelinen acceptera i ett riktigt system?
    if not isinstance(value, str):
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
