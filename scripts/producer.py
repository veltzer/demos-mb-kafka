#!/usr/bin/env python

"""
producer script
"""

from confluent_kafka import Producer

bootstrap_servers = "localhost:29092"
topic_name = "test-topic"
message_to_send = "Hello from Python Confluent Kafka Producer!"


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print("Message sent successfully!")
        print(f"Topic: {msg.topic()}")
        print(f"Partition: {msg.partition()}")
        print(f"Offset: {msg.offset()}")


def main():
    print(f"Configuring producer for Kafka broker at {bootstrap_servers}...")

    producer_conf = {
        "bootstrap.servers": bootstrap_servers,
    }

    producer = Producer(producer_conf)

    print("Producer configured.")

    print(f"Sending message to topic [{topic_name}]: [{message_to_send}]")

    producer.produce(
        topic_name,
        value=message_to_send.encode("utf-8"),
        callback=delivery_report
    )

    print("\nFlushing messages and waiting for delivery reports...")
    remaining_messages = producer.flush(timeout=10)

    if remaining_messages > 0:
        print(f"WARN: {remaining_messages} message(s) were not delivered")

    print("Producer operations finished.")


if __name__ == "__main__":
    main()
