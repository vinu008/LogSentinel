import json
import os
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import db

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "logs.raw")

def connect_consumer(max_retries=10, retry_delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                group_id="storage-service",
            )
            return consumer
        except NoBrokersAvailable:
            print(f"Kafka not ready, retrying ({attempt}/{max_retries}) in {retry_delay}s...")
            time.sleep(retry_delay)
    raise Exception("Could not connect to Kafka after max retries")

def run():
    db.init_db()
    print(f"Storage service started. Consuming from topic: {KAFKA_TOPIC}")
    consumer = connect_consumer()
    for message in consumer:
        event = message.value
        try:
            db.insert_log(event)
            print(f"Stored log from service={event['service']} level={event['level']}")
        except Exception as e:
            print(f"Failed to store log: {e}")

if __name__ == "__main__":
    run()
