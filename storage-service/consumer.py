import json
import os
from kafka import KafkaConsumer
import db

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "logs.raw")

def run():
    db.init_db()
    print(f"Storage service started. Consuming from topic: {KAFKA_TOPIC}")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="storage-service",
    )
    for message in consumer:
        event = message.value
        try:
            db.insert_log(event)
            print(f"Stored log from service={event['service']} level={event['level']}")
        except Exception as e:
            print(f"Failed to store log: {e}")

if __name__ == "__main__":
    run()
