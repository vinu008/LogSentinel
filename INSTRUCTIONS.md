# LogSentinel — INSTRUCTIONS.md

## What is LogSentinel?
Self-hostable distributed log aggregation and anomaly detection. Ingests structured JSON log
events, stores them, and detects anomalous patterns using rolling Z-score statistics.

## Repo Structure
```
LogSentinel/
├── ingestion-service/   # FastAPI app — accepts log events, publishes to Kafka
├── storage-service/     # Kafka consumer — writes logs to SQLite
├── anomaly-engine/      # Rolling Z-score anomaly detection (in progress)
├── alert-dispatcher/    # Slack/email alerts (planned)
├── dashboard/           # React frontend (planned)
├── docs/demo.md         # End-to-end demo walkthrough
└── docker-compose.yml
```

## How to Run
```bash
docker compose up --build
```

## How to Test
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-03-01T12:00:00Z", "service": "auth-service", "level": "ERROR", "message": "DB connection failed"}'
```

## Log Schema
```json
{
  "timestamp": "2026-03-01T12:00:00Z",
  "service":   "auth-service",
  "level":     "ERROR",
  "message":   "Something happened",
  "metadata":  {"key": "value"}
}
```

## Kafka Topics
| Topic | Purpose |
|-------|---------|
| `logs.raw` | All ingested log events |
| `logs.anomalies` | Anomaly events from anomaly engine |

## Current Status
| Service | Status |
|---------|--------|
| ingestion-service | Complete |
| storage-service | Complete |
| anomaly-engine | In progress |
| alert-dispatcher | Planned |
| dashboard | Planned |
