# LogSentinel

Distributed log aggregation and real-time anomaly detection system.

## Architecture

Five microservices communicating over Kafka and REST:

- **ingestion-service** — FastAPI REST API that accepts structured JSON log events and publishes them to Kafka
- **storage-service** — Kafka consumer that persists logs to ClickHouse and exposes a Query API
- **anomaly-engine** — Streaming anomaly detection using rolling Z-score statistics
- **alert-dispatcher** — Rule-based alert evaluation and Slack/email notification dispatch
- **dashboard** — React frontend with live log stream, anomaly timeline, and alert history

## Tech Stack

- Python / FastAPI
- Apache Kafka
- ClickHouse (columnar log storage)
- Redis (rolling window buffer)
- React
- Docker Compose

## Getting Started

```bash
docker compose up
```

> Full service implementation in progress. See milestone chart in project checkpoint report.

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
