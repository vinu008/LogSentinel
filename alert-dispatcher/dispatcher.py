import json
import os
import time
import urllib.request
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ANOMALY_TOPIC = os.getenv("ANOMALY_TOPIC", "logs.anomalies")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "60"))

last_alert_time = {}  # service -> timestamp

def send_slack(message: str):
    if not SLACK_WEBHOOK_URL:
        print(f"[SLACK] {message}")
        return
    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)

def run():
    consumer = KafkaConsumer(
        ANOMALY_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="alert-dispatcher",
    )

    print(f"Alert dispatcher started. Consuming from: {ANOMALY_TOPIC}")

    for message in consumer:
        anomaly = message.value
        service = anomaly["service"]
        now = time.time()

        # enforce cooldown
        if service in last_alert_time and now - last_alert_time[service] < COOLDOWN_SECONDS:
            print(f"Cooldown active for {service}, skipping alert")
            continue

        last_alert_time[service] = now
        msg = (
            f":warning: *Anomaly detected in `{service}`*\n"
            f"Error rate: {anomaly['error_rate']} (mean: {anomaly['mean']}, "
            f"Z-score: {anomaly['zscore']})"
        )
        send_slack(msg)
        print(f"Alert sent for {service}")

if __name__ == "__main__":
    run()
