#!/usr/bin/env python

"""
Consumer script
"""

from confluent_kafka import Consumer, KafkaException

bootstrap_servers = "localhost:29092"
topic_name = "test-topic"
consumer_group_id = "my-consumer-group"


def main():
    print(f"Setting up consumer for Kafka broker at {bootstrap_servers}...")

    consumer_conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": consumer_group_id,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(consumer_conf)
    print(f"Consumer configured with group ID [{consumer_group_id}]")

    consumer.subscribe([topic_name])
    print(f"Subscribed to topic [{topic_name}] Waiting for messages...")

    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        raw_key = msg.key()
        key = raw_key.decode("utf-8") if raw_key else "None"
        raw_value = msg.value()
        value = raw_value.decode("utf-8") if raw_value is not None else "None"
        print("Message received successfully!")
        print(f"Topic: {msg.topic()}")
        print(f"Partition: {msg.partition()}")
        print(f"Offset: {msg.offset()}")
        print(f"Key: {key}")
        print(f"Value: {value}")


if __name__ == "__main__":
    main()
