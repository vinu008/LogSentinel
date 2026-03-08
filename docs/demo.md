# LogSentinel — Local Demo

## Running the full stack
```bash
docker compose up --build
```
Wait ~20 seconds for Kafka to start. You'll see the storage service print
`Storage service started. Consuming from topic: logs.raw` when ready.

## Sending a test log event
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-03-01T12:00:00Z",
    "service": "auth-service",
    "level": "ERROR",
    "message": "Failed to connect to database",
    "metadata": {"host": "prod-01", "trace_id": "abc123"}
  }'
```
Expected response: `{"status": "accepted"}`

The storage service will print: `Stored log from service=auth-service level=ERROR`

## Sending a batch
```bash
curl -X POST http://localhost:8000/ingest/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"timestamp": "2026-03-01T12:00:01Z", "service": "auth-service", "level": "INFO", "message": "User login successful"},
    {"timestamp": "2026-03-01T12:00:02Z", "service": "payment-service", "level": "WARN", "message": "Slow response time"}
  ]'
```
Expected response: `{"status": "accepted", "count": 2}`
