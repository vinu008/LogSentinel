# LogSentinel Benchmark Results

## Environment
- MacBook Air M2, 16GB RAM
- Docker Desktop (4 CPUs, 8GB memory allocated)
- All services running via docker compose

## Ingestion Throughput
- Total events sent: 1,000
- Batch size: 50 events/request
- **Result: 1,686 events/sec**

## Storage Latency
- Measured as time from POST /ingest/batch to event appearing in GET /logs
- 5 trials
- **Median: 138ms | Min: 136ms | Max: 446ms**

## Anomaly Detection Latency
- Measured as time from injecting high error-rate burst to anomaly event
  appearing in logs.anomalies Kafka topic
- **Observed: ~3-5 seconds** (dominated by rolling window needing MIN_SAMPLES=10)

## Notes
- Throughput is bottlenecked by Kafka running in Docker on a local machine,
  not by the ingestion service itself
- Detection latency depends on WINDOW_SIZE and MIN_SAMPLES config values;
  reducing MIN_SAMPLES from 10 to 5 halves detection latency at the cost
  of more false positives
