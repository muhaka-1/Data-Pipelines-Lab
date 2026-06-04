from datetime import datetime
from flask import Flask, jsonify, request
from db import get_metrics, insert_raw_event, list_raw_events

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ingestion-api"})


@app.post("/events")
def create_event():
    payload = request.get_json(silent=True)

    # TODO Övning 1: Print payload to see what data looks like before saving
    print("Incoming payload:", payload)

    if payload is None:
        return jsonify({"error": "Request body måste vara JSON"}), 400

    # TODO Övning 1: Reject empty JSON {}
    if not payload:
        return jsonify({"error": "Payload får inte vara tomt"}), 400

    raw_event = insert_raw_event(payload)
    return jsonify(raw_event), 202


@app.get("/events")
def get_events():
    limit = request.args.get("limit", default=20, type=int)
    return jsonify(list_raw_events(limit=limit)), 200


@app.get("/metrics")
def metrics():
    data = get_metrics()
    # TODO Övning 2: Add timestamp to metrics response
    data["timestamp"] = datetime.utcnow().isoformat()
    return jsonify(data), 200


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True),