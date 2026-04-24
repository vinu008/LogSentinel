# LogSentinel — INSTRUCTIONS.md

## What is LogSentinel?
Self-hostable distributed log aggregation and anomaly detection. Ingests structured JSON log
events, stores them, and detects anomalous patterns using rolling Z-score statistics.

## Repo Structure
```
LogSentinel/
├── ingestion-service/   # FastAPI app — accepts log events, publishes to Kafka
├── storage-service/     # Kafka consumer — writes logs to SQLite
├── anomaly-engine/      # Rolling Z-score anomaly detection
├── alert-dispatcher/    # Slack/email alerts
├── dashboard/           # React frontend with live log stream and anomaly panel
├── load-generator/      # Traffic simulator and benchmark suite
├── docs/demo.md         # End-to-end demo walkthrough
├── docs/bench_results.md # Benchmark results
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
| anomaly-engine | Complete |
| alert-dispatcher | Complete |
| dashboard | Complete |
| load-generator | Complete |

## Running Benchmarks

```bash
# Make sure docker compose is up first
docker-compose up --build

# Run the benchmark suite
cd load-generator
python benchmark.py
```

Results will print to stdout. Save them to docs/bench_results.md.

## Demo Sequence (for presentations)

1. `docker-compose up --build`
2. Open dashboard at http://localhost:3000
3. In a separate terminal: `python load-generator/generate.py --rate 10 --anomaly-service auth-service --anomaly-duration 60`
4. Watch logs populate in the dashboard
5. After 30 seconds, anomaly panel activates and Slack alert fires
