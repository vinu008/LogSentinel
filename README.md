# LogSentinel

Distributed log aggregation and real-time anomaly detection system.

## Architecture

Five microservices communicating over Kafka and REST:

- **ingestion-service** — FastAPI REST API that accepts structured JSON log events and publishes them to Kafka
- **storage-service** — Kafka consumer that persists logs to SQLite
- **anomaly-engine** — Streaming anomaly detection using rolling Z-score statistics
- **alert-dispatcher** — Rule-based alert evaluation and Slack/email notification dispatch
- **dashboard** — React frontend with live log stream, anomaly timeline, and alert history

## Tech Stack

- Python / FastAPI
- Apache Kafka
- SQLite (log storage)
- React (planned)
- Docker Compose

## Getting Started

```bash
docker-compose up --build zookeeper kafka ingestion-service storage-service anomaly-engine alert-dispatcher
```

See [docs/demo.md](docs/demo.md) for a full end-to-end demo walkthrough.

## End-to-End Test Results

### Ingestion (POST /ingest)
```
$ curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-03-01T12:00:00Z", "service": "auth-service", "level": "ERROR", "message": "Failed to connect to database", "metadata": {"host": "prod-01", "trace_id": "abc123"}}'

{"status":"accepted"}
```
Docker logs confirmed:
```
storage-service-1  | Stored log from service=auth-service level=ERROR
```

### Query API (GET /logs)
```
$ curl "http://localhost:8001/logs?service=auth-service"

{
  "logs": [
    {"id": 10, "timestamp": "2026-03-01T12:00:15Z", "service": "auth-service", "level": "ERROR", "message": "Test error 15", "metadata": null},
    {"id": 9, "timestamp": "2026-03-01T12:00:14Z", "service": "auth-service", "level": "ERROR", "message": "Test error 14", "metadata": null},
    {"id": 8, "timestamp": "2026-03-01T12:00:13Z", "service": "auth-service", "level": "ERROR", "message": "Test error 13", "metadata": null},
    {"id": 7, "timestamp": "2026-03-01T12:00:12Z", "service": "auth-service", "level": "ERROR", "message": "Test error 12", "metadata": null},
    {"id": 6, "timestamp": "2026-03-01T12:00:11Z", "service": "auth-service", "level": "ERROR", "message": "Test error 11", "metadata": null},
    {"id": 5, "timestamp": "2026-03-01T12:00:10Z", "service": "auth-service", "level": "ERROR", "message": "Test error 10", "metadata": null},
    {"id": 4, "timestamp": "2026-03-01T12:00:00Z", "service": "auth-service", "level": "ERROR", "message": "Failed to connect to database", "metadata": "{\"host\": \"prod-01\", \"trace_id\": \"abc123\"}"},
    ...
  ],
  "count": 10
}
```

## Log Schema

All services conform to the following JSON log event schema:

```json
{
  "timestamp": "2026-02-20T12:00:00Z",
  "service": "auth-service",
  "level": "ERROR",
  "message": "Failed to connect to database",
  "metadata": {
    "host": "prod-01",
    "trace_id": "abc123"
  }
}
```
