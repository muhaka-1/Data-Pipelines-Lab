# Jensen Data Pipelines - Övningar

## Syfte

Syftet är att förstå hur ett IoT-dataflöde kan byggas från sensor till databas, och hur pipelinen kan göras robust när dataformat, nätverk och enheter inte beter sig perfekt.

Efter övningarna ska ni kunna förklara:

- skillnaden mellan rådata och bearbetad data
- varför pipelines behöver validering
- varför idempotens behövs vid retries och dubletter
- hur dead-letter-lagring hjälper felsökning
- vilka metrics som visar om ett dataflöde fungerar

## Scenario

Ni bygger ett system för smarta byggnader.

Sensorer skickar temperatur, luftfuktighet och tidsstämpel. Fastighetsägaren vill kunna se historik, upptäcka fel och få larm om dataflödet slutar fungera.

I föreläsningen nämns också rörelse, live-status och larm som exempel på vad ett smart byggnadssystem kan behöva. I den här labben fokuserar vi på temperatur, luftfuktighet och tidsstämpel för att hålla kodbasen liten.

---

## Lektionsupplägg

Övningarna är uppdelade i två arbetspass:

- Förmiddag: 1 timme och 30 minuter
- Eftermiddag: 1 timme och 30 minuter

Tiderna är ungefärliga. Om ni fastnar på Docker, databasanslutning eller SQL räcker det att göra grunduppgifterna. Extra-frågorna och extra-utmaningarna finns för studenter som blir klara tidigt.

I slidesen finns också gemensam genomgång före lunch och summering i slutet av dagen. De delarna ligger utanför de två praktiska övningspassen.

Arbeta individuellt med övningarna. Efter övningspassen går vi igenom viktiga observationer och lösningar gemensamt.

### Förmiddag - 1 timme och 30 minuter

Mål för förmiddagen:

- starta hela miljön
- skicka sensor-events till API:t
- förstå vad rådata är
- undersöka `raw_events`
- beskriva hela dataflödet på en övergripande nivå

Rekommenderad tidsfördelning:

- Uppgift 1: 10 minuter
- Uppgift 2: 20 minuter
- Uppgift 3: 20 minuter
- Uppgift 4: 25 minuter
- Uppgift 5 och Testa själv först 1: 15 minuter

## Övning 1 - Från sensor till rådata

### Mini-exempel - vad är pipelinen här?

I den här kodbasen börjar vi med en mycket enkel pipeline.

```text
simulator
API
raw_events
```

Det betyder:

- `simulator` låtsas vara sensorer
- `API` tar emot sensor-events
- `raw_events` sparar det som kom in

Först fokuserar vi bara på att ta emot och spara data. Bearbetning, validering och felhantering kommer senare.

### Mini-exempel - ett event

Ett sensor-event kan se ut så här:

```json
{
  "eventId": "manual-1",
  "deviceId": "sensor-1",
  "temperature": 21.5,
  "humidity": 45,
  "timestamp": "2026-06-03T09:00:00Z"
}
```

När eventet kommer in sparas hela JSON-objektet i tabellen `raw_events`.

### Uppgift 1 - Starta miljön

```bash
docker compose up --build db api
```

Verifiera att API och databas startar.

```bash
curl http://localhost:5002/health
```

### Uppgift 2 - Skicka ett sensor-event

```bash
curl -i -X POST http://localhost:5002/events \
  -H "Content-Type: application/json" \
  -d '{"eventId":"manual-1","deviceId":"sensor-1","temperature":21.5,"humidity":45,"timestamp":"2026-06-03T09:00:00Z"}'
```

Testa själv:

- Varför returnerar API:t `202 Accepted` och inte `201 Created`?
- Vad betyder det att datat bara är mottaget, inte färdigbearbetat?

Skriv ner ett kort svar.

Koduppgift:

Öppna `api/app.py` och leta efter `TODO Övning 1`.

Testa att:

- skriva ut inkommande payload med `print(payload)`
- skicka ett tomt JSON-objekt `{}`
- ta ställning till om API:t ska spara all rådata eller stoppa vissa requests direkt

### Uppgift 3 - Utforska rådata

Anslut till databasen:

```bash
docker exec -it jensen-pipeline-db psql -U student -d datapipeline
```

Kör:

```sql
SELECT id, event_id, payload, status, received_at
FROM raw_events
ORDER BY id;
```

Testa själv först:

- Vad sparas exakt?
- Vilken information är viktig för felsökning?
- Vilka fält kommer från sensorn och vilka skapas av systemet?

Skriv ner dina observationer.

### Uppgift 4 - Kör simulatorn

I en ny terminal:

```bash
docker compose run --rm simulator
```

Titta på inkomna events:

```bash
curl http://localhost:5002/events
```

Koduppgift:

Öppna `api/app.py` och `api/db.py`.

Testa att `/events` kan ta emot en frågeparameter:

```text
/events?limit=5
```

Målet är att studenterna ska se att API:et inte alltid behöver returnera all data.

Testa:

```bash
curl http://localhost:5002/events?limit=2
curl http://localhost:5002/events?limit=100
curl http://localhost:5002/events?limit=abc
```

Testa själv först:

- Vad händer om `limit` saknas?
- Vad händer om `limit` inte är ett nummer?
- Varför begränsar koden maxvärdet till 100?

Skriv ner vad du tror händer innan du testar, och kontrollera sedan mot resultatet.

### Uppgift 5 - Förstå dataflödet

Beskriv flödet som kodbasen representerar med egna ord.

Utgå från:

- sensor-simulator
- ingestion API
- raw_events
- pipeline-worker
- readings
- dead_letter_events
- metrics

Testa själv först:

- Vilket steg är source?
- Vilket steg är ingestion?
- Vilket steg är processing?
- Vilket steg är storage?
- Var syns monitoring?

Skriv ett eget svar med egna ord.

Extra om ni blir klara tidigt:

Rita flödet på papper eller i ett digitalt verktyg (Miro, draw.io).

### Extra-frågor

Testa följande:

- Vad händer om ni skickar `{}` till `POST /events`?
- Vad händer om `eventId` saknas?
- Vad händer om `deviceId` saknas?
- Vad händer om `temperature` är text, till exempel `"warm"`?
- Vad är skillnaden mellan databasens `id` och eventets `event_id`?
- Varför sparas hela meddelandet i `payload`?
- Vilken kolumn visar när API:t tog emot datat?
- Ska API:t stoppa uppenbart fel data direkt, eller ska allt sparas som rådata?
- Vad skulle ni behöva logga om kunden säger: "dashboarden är tom"?
- Vilken endpoint skulle ni titta på först: `/events` eller `/metrics`?


Extra SQL:

```sql
SELECT status, COUNT(*)
FROM raw_events
GROUP BY status;
```

```sql
SELECT payload->>'deviceId' AS device_id, COUNT(*)
FROM raw_events
GROUP BY device_id
ORDER BY COUNT(*) DESC;
```

---

## Djupdyk - Var kan flödet gå sönder?

Svara individuellt:

- Vad händer om API:t är nere?
- Vad händer om databasen är nere?
- Vad händer om sensorn skickar fel format?
- Vad händer om samma event skickas två gånger?
- Hur vet vi att pipelinen inte bearbetar data?

---

### Eftermiddag - 1 timme och 30 minuter

Mål för eftermiddagen:

- köra pipeline-workern
- förstå validering och dead-letter-lagring
- hantera ändrade dataformat
- förstå retries, dubletter och idempotens
- läsa och bygga ut metrics

Rekommenderad tidsfördelning:

- Uppgift 6: 15 minuter
- Uppgift 7: 20 minuter
- Uppgift 8: 20 minuter
- Uppgift 9: 15 minuter
- Uppgift 10 och Djupdyk - Designbeslut: 20 minuter

## Övning 2 - Gör pipelinen robust

### Uppgift 6 - Kör pipeline-workern

På förmiddagen körde ni bara databas och API. Nu ska ni köra pipeline-workern som bearbetar rådata.

Kör den manuellt en gång om ni vill se output direkt:

```bash
docker compose run --rm pipeline python worker.py --once
```

Vill ni låta pipelinen fortsätta köra automatiskt efteråt:

```bash
docker compose up -d pipeline
```

Undersök resultatet:

```sql
SELECT id, event_id, device_id, temperature, humidity, measured_at
FROM readings
ORDER BY id;
```

```sql
SELECT id, event_id, error_message, payload
FROM dead_letter_events
ORDER BY id;
```

```sql
SELECT id, event_id, status, error_message
FROM raw_events
ORDER BY id;
```

### Uppgift 7 - Förstå valideringen

Öppna:

```text
pipeline/validation.py
```

Besvara:

- Vilka fält krävs?
- Vilka datatyper krävs?
- Vilka värden räknas som orimliga?
- Vilka fel hamnar i dead-letter?

Koduppgift:

Leta efter `TODO Övning 2` i `pipeline/validation.py`.

Minst en av dessa bör göras:

- acceptera både `temperature` och `temp`
- lägga till rimlighetskontroll för temperatur
- testa olika timestamp-format

### Uppgift 8 - Incident: `temp` istället för `temperature`

Simulatorn skickar ett event där firmware har bytt fältnamn:

```json
{
  "eventId": "evt-1004",
  "deviceId": "sensor-lab-2",
  "temp": 22.0,
  "humidity": 44,
  "timestamp": "2026-06-03T09:15:00Z"
}
```

Testa själv först:

- Var upptäcks felet?
- Vad händer med eventet?
- Hur skulle ni göra pipelinen bakåtkompatibel?

Skriv ner din hypotes innan du ändrar koden.

Kodutmaning:

Ändra `pipeline/validation.py` så att pipelinen accepterar både `temperature` och `temp`.

Tips:

Det här kräver troligen att ni inte längre kräver `temperature` på exakt samma sätt i `REQUIRED_FIELDS`.

### Uppgift 9 - Dubletter och idempotens

Simulatorn skickar `evt-1002` två gånger.

Tänk på detta som ett enkelt retry-scenario:

1. sensorn skickar eventet
2. API:t tar emot eventet
3. sensorn är osäker på om allt gick bra
4. samma event skickas igen

Undersök:

```sql
SELECT event_id, COUNT(*)
FROM raw_events
GROUP BY event_id
ORDER BY event_id;
```

```sql
SELECT event_id, COUNT(*)
FROM readings
GROUP BY event_id
ORDER BY event_id;
```

Testa själv först:

- Varför finns dubletten i `raw_events`?
- Varför ska den inte skapa två rader i `readings`?
- Vad betyder idempotens i den här pipelinen?
- Varför kan retries skapa dubletter?

Skriv ett kort svar med egna ord.

Koduppgift:

Öppna `pipeline/worker.py`.

Leta efter TODO-kommentaren om dubletter.

Testa själv först:

- är duplicate ett fel?
- är duplicate ett normalt retry-beteende?
- ska duplicate sparas i dead-letter eller bara markeras?

Ta ställning och skriv ner varför.

### Uppgift 10 - Metrics

Testa:

```bash
curl http://localhost:5002/metrics
```

Testa själv först:

- Vilka mätvärden finns?
- Vilken metric visar att pipelinen ligger efter?
- Vilken metric visar att dataformatet kanske ändrats?
- Vilken metric skulle ni larma på?

Kodutmaning:

Bygg ut `api/db.py` och `/metrics` så att svaret också visar:

- senaste mottagna event
- senaste processade event
- antal events per status

Leta efter `TODO Övning 2` i `api/db.py`.

Extra:

- antal events per device
- andel failed events i procent

---

## Djupdyk - Designbeslut

Besvara individuellt först:

- Vad sparas som rådata?
- Vad sparas som kuraterad data?
- Vilka fel löses automatiskt?
- Vilka fel kräver manuell felsökning?
- Vilka larm skulle ni sätta upp i produktion?
- Skulle ni välja batch, streaming eller hybrid för ett riktigt IoT-system?

Skriv ner dina beslut och motivera kort varför.

Förbered en summering på 2 minuter:

- beskriv er pipeline
- nämn de viktigaste lagringstabellerna
- säg om ni skulle välja batch, streaming eller hybrid i ett riktigt system
- lyft tre risker
- förklara hur ni skulle upptäcka och återställa fel

---

## Extra utmaningar

### 1. Lägg till en ny sensor

Lägg till events för en ny sensor i `simulator/simulator.py`.

### 2. Lägg till avvikelselarm

Markera temperaturer över 28 grader som avvikande.

Välj själv om avvikelsen ska:

- sparas i en ny tabell
- skrivas i loggen
- synas i `/metrics`

Tips:

Det finns en `TODO Extra` i `pipeline/worker.py` för detta.

### 3. Lägg till batch-körning

Ändra workern så att den processar max 3 events per körning.

Testa själv först:

- Vad händer om events kommer in snabbare än pipelinen hinner bearbeta?
- Hur syns det i metrics?

Tips:

Det finns en `TODO Extra` i `pipeline/worker.py` om `BATCH_SIZE`.
