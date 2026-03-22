import json
import os
from kafka import KafkaConsumer, KafkaProducer
from detector import AnomalyDetector

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "logs.raw")
ANOMALY_TOPIC = os.getenv("ANOMALY_TOPIC", "logs.anomalies")

def run():
    detector = AnomalyDetector()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="anomaly-engine",
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    print(f"Anomaly engine started. Consuming from: {KAFKA_TOPIC}")

    for message in consumer:
        event = message.value
        anomaly = detector.record(event["service"], event["level"])
        if anomaly:
            print(f"Anomaly detected: {anomaly}")
            producer.send(ANOMALY_TOPIC, value=anomaly)
            producer.flush()

if __name__ == "__main__":
    run()
