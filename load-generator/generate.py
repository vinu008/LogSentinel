import argparse
import json
import random
import time
import urllib.request

INGESTION_URL = "http://localhost:8000/ingest/batch"

SERVICES = ["auth-service", "payment-service", "inventory-service", "api-gateway"]

NORMAL_MESSAGES = {
    "INFO":  ["User login successful", "Request processed", "Cache hit", "Health check OK"],
    "DEBUG": ["Query executed in 12ms", "Session refreshed", "Config reloaded"],
    "WARN":  ["Slow query detected", "Retry attempt 1", "Memory usage above 70%"],
    "ERROR": ["Connection timeout", "Invalid token", "Database write failed"],
}

def make_event(service: str, force_error: bool = False):
    if force_error or random.random() < 0.05:  # 5% normal error rate
        level = "ERROR"
    elif random.random() < 0.1:
        level = "WARN"
    elif random.random() < 0.3:
        level = "DEBUG"
    else:
        level = "INFO"
    messages = NORMAL_MESSAGES.get(level, ["Unknown event"])
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "service": service,
        "level": level,
        "message": random.choice(messages),
        "metadata": {"host": f"{service}-pod-{random.randint(1,3)}"},
    }

def send_batch(events: list):
    payload = json.dumps(events).encode("utf-8")
    req = urllib.request.Request(
        INGESTION_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Failed to send batch: {e}")

def run(rate: int, anomaly_service: str, anomaly_duration: int):
    print(f"Load generator started. Rate: {rate} events/sec across {len(SERVICES)} services.")
    if anomaly_service:
        print(f"Will inject anomaly on '{anomaly_service}' for {anomaly_duration}s starting in 30s.")

    start = time.time()
    anomaly_start = start + 30  # inject anomaly after 30s warmup
    anomaly_end = anomaly_start + anomaly_duration

    while True:
        now = time.time()
        in_anomaly = anomaly_service and anomaly_start <= now <= anomaly_end

        batch = []
        for _ in range(rate):
            service = random.choice(SERVICES)
            force_error = in_anomaly and service == anomaly_service and random.random() < 0.7
            batch.append(make_event(service, force_error=force_error))

        send_batch(batch)
        if in_anomaly:
            print(f"[ANOMALY ACTIVE] Injecting high error rate on {anomaly_service}")
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=int, default=10, help="Events per second")
    parser.add_argument("--anomaly-service", type=str, default="auth-service")
    parser.add_argument("--anomaly-duration", type=int, default=60, help="Anomaly window in seconds")
    args = parser.parse_args()
    run(args.rate, args.anomaly_service, args.anomaly_duration)
