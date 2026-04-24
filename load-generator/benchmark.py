import json
import time
import urllib.request
import threading
import statistics

INGESTION_URL = "http://localhost:8000/ingest/batch"
QUERY_URL = "http://localhost:8001/logs"

def send_batch(events):
    payload = json.dumps(events).encode("utf-8")
    req = urllib.request.Request(
        INGESTION_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def make_event(service, level="INFO"):
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "service": service,
        "level": level,
        "message": f"benchmark event from {service}",
    }

def benchmark_throughput(total_events=1000, batch_size=50):
    """Measure how many events/sec the ingestion service can handle."""
    print(f"\n=== Throughput Benchmark ===")
    print(f"Sending {total_events} events in batches of {batch_size}...")

    batches = [
        [make_event("bench-service") for _ in range(batch_size)]
        for _ in range(total_events // batch_size)
    ]

    start = time.time()
    for batch in batches:
        send_batch(batch)
    elapsed = time.time() - start

    throughput = total_events / elapsed
    print(f"Sent {total_events} events in {elapsed:.2f}s")
    print(f"Throughput: {throughput:.1f} events/sec")
    return throughput

def benchmark_latency(num_trials=5):
    """
    Measure time from sending a burst of ERROR events (anomaly injection)
    to the anomaly appearing in the storage layer.
    We approximate this by checking when the events are queryable.
    """
    print(f"\n=== Latency Benchmark ===")
    print(f"Running {num_trials} trials...")
    latencies = []

    for trial in range(num_trials):
        service = f"latency-trial-{trial}"
        # send 20 error events to trigger anomaly detection
        batch = [make_event(service, level="ERROR") for _ in range(20)]

        t0 = time.time()
        send_batch(batch)

        # poll query API until events appear
        found = False
        for _ in range(60):  # poll for up to 6 seconds
            time.sleep(0.1)
            try:
                url = f"{QUERY_URL}?service={service}&limit=1"
                res = urllib.request.urlopen(url, timeout=2)
                data = json.loads(res.read())
                if data["count"] > 0:
                    latency = time.time() - t0
                    latencies.append(latency)
                    print(f"  Trial {trial+1}: {latency*1000:.0f}ms")
                    found = True
                    break
            except Exception:
                pass
        if not found:
            print(f"  Trial {trial+1}: timeout")

        time.sleep(1)  # cooldown between trials

    if latencies:
        print(f"\nMedian storage latency: {statistics.median(latencies)*1000:.0f}ms")
        print(f"Min: {min(latencies)*1000:.0f}ms  Max: {max(latencies)*1000:.0f}ms")
    return latencies

if __name__ == "__main__":
    print("LogSentinel Benchmark Suite")
    print("Make sure docker compose is running before starting.\n")
    time.sleep(1)

    throughput = benchmark_throughput(total_events=1000, batch_size=50)
    latencies = benchmark_latency(num_trials=5)

    print("\n=== Summary ===")
    print(f"Ingestion throughput:     {throughput:.0f} events/sec")
    if latencies:
        print(f"Median storage latency:   {statistics.median(latencies)*1000:.0f}ms")
    print("\nSave these numbers to docs/bench_results.md")
