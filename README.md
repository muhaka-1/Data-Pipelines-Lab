# Jensen Data Pipelines Lab

Starter codebase för lektionen om data pipelines.

Ni arbetar med ett förenklat IoT-scenario:

- sensorer skickar mätvärden
- ett API tar emot events
- rådata sparas i PostgreSQL
- en pipeline-worker bearbetar events
- godkända mätvärden sparas i en kuraterad tabell
- felaktiga events hamnar i dead-letter-lagring

## Arkitektur

```text
sensor-simulator
ingestion-api
PostgreSQL raw_events
pipeline-worker
readings
dead_letter_events
```

## Tjänster

- `db` - PostgreSQL
- `api` - Flask API som tar emot sensor-events
- `pipeline` - Python-worker som bearbetar rådata
- `simulator` - Python-klient som skickar test-events

## Starta för förmiddagsövningen

Kör från projektets rot:

```bash
docker compose up --build db api
```

API:t finns på:

```text
http://localhost:5002
```

Förmiddagen fokuserar på ingestion och rådata. Därför startas inte pipeline-workern direkt.

## Testa API:t

```bash
curl http://localhost:5002/health
curl http://localhost:5002/events
curl http://localhost:5002/metrics
```

Skicka ett event manuellt:

```bash
curl -i -X POST http://localhost:5002/events \
  -H "Content-Type: application/json" \
  -d '{"eventId":"manual-1","deviceId":"sensor-1","temperature":21.5,"humidity":45,"timestamp":"2026-06-03T09:00:00Z"}'
```

## Kör simulatorn

I en ny terminal:

```bash
docker compose run --rm simulator
```

## Kör pipelinen en gång

Eftermiddagen fokuserar på bearbetning, validering, dead-letter och metrics.

Kör pipelinen manuellt en gång:

```bash
docker compose run --rm pipeline python worker.py --once
```

Vill du låta pipelinen fortsätta köra automatiskt:

```bash
docker compose up -d pipeline
```

Vill du starta alla tjänster samtidigt efter att du förstått flödet:

```bash
docker compose up --build
```

## Anslut till databasen

```bash
docker exec -it jensen-pipeline-db psql -U student -d datapipeline
```

Bra SQL-frågor:

```sql
SELECT * FROM raw_events ORDER BY id;
SELECT * FROM readings ORDER BY id;
SELECT * FROM dead_letter_events ORDER BY id;
SELECT status, COUNT(*) FROM raw_events GROUP BY status;
```

## Koddelar i labben

### Förmiddag

Förstå och komplettera ingestion:

- `POST /events`
- spara rådata i `raw_events`
- lista inkomna events
- förstå skillnaden mellan rådata och bearbetad data
- jobba med `TODO Övning 1`

Filer:

- `api/app.py`
- `api/db.py`

### Eftermiddag

Gör pipelinen robust:

- validera schema
- stoppa orimliga värden
- hantera dubletter med `eventId`
- skicka trasiga events till dead-letter
- exponera enkla metrics
- jobba med `TODO Övning 2`

Filer:

- `pipeline/worker.py`
- `pipeline/validation.py`
- `api/db.py`
- `api/app.py`

## Stoppa

```bash
docker compose down
```

Ta även bort databasen:

```bash
docker compose down -v
```
