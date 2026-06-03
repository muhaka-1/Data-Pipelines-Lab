from flask import Flask, jsonify, request

from db import get_metrics, insert_raw_event, list_raw_events

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ingestion-api"})


@app.post("/events")
def create_event():
    """
    Övning 1:
    API:t tar emot sensor-events och sparar dem som rådata.

    Övning 2:
    Diskutera vad som ska valideras redan här och vad som kan vänta till pipelinen.
    """
    payload = request.get_json(silent=True)

    # TODO Övning 1:
    # Skriv ut inkommande payload i terminalen med print(payload).
    # Fråga: hur ser datat ut innan det sparas i databasen?

    if payload is None:
        return jsonify({"error": "Request body måste vara JSON"}), 400

    # TODO Övning 1:
    # Testa att skicka {} och fundera på om API:t ska acceptera det.
    # Just nu sparar API:t all JSON som rådata.

    raw_event = insert_raw_event(payload)

    return jsonify(raw_event), 202


@app.get("/events")
def get_events():
    limit = request.args.get("limit", default=20, type=int)

    # Extra Övning 1:
    # Testa /events?limit=5 och jämför med /events.
    # Fråga: varför vill vi ibland begränsa hur mycket data API:t returnerar?
    return jsonify(list_raw_events(limit=limit)), 200


@app.get("/metrics")
def metrics():
    """
    Övning 2:
    Bygg gärna ut detta med fler metrics, till exempel:
    - senaste mottagna event
    - senaste processade event
    - antal events per device
    """
    # TODO Övning 2:
    # När get_metrics() byggs ut, kontrollera att API-svaret fortfarande är lätt att läsa.
    return jsonify(get_metrics()), 200


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
