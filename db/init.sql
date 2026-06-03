DROP TABLE IF EXISTS dead_letter_events;
DROP TABLE IF EXISTS readings;
DROP TABLE IF EXISTS raw_events;

CREATE TABLE raw_events (
  id SERIAL PRIMARY KEY,
  event_id TEXT,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'new',
  error_message TEXT,
  received_at TIMESTAMP NOT NULL DEFAULT NOW(),
  processed_at TIMESTAMP
);

CREATE TABLE readings (
  id SERIAL PRIMARY KEY,
  event_id TEXT NOT NULL UNIQUE,
  device_id TEXT NOT NULL,
  temperature NUMERIC(5, 2) NOT NULL,
  humidity NUMERIC(5, 2) NOT NULL,
  measured_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE dead_letter_events (
  id SERIAL PRIMARY KEY,
  raw_event_id INT REFERENCES raw_events(id),
  event_id TEXT,
  payload JSONB NOT NULL,
  error_message TEXT NOT NULL,
  failed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_raw_events_status ON raw_events(status);
CREATE INDEX idx_raw_events_event_id ON raw_events(event_id);
CREATE INDEX idx_readings_device_id ON readings(device_id);
