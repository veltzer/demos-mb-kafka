#!/usr/bin/env python

from confluent_kafka import Consumer, KafkaError, KafkaException

bootstrap_servers = 'localhost:29092'
topic_name = 'test-topic'
consumer_group_id = 'my-consumer-group'

def main():
    print(f"Attempting to configure consumer for Kafka broker at {bootstrap_servers}...")

    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': consumer_group_id,
        'auto.offset.reset': 'earliest',
    }

    consumer = Consumer(consumer_conf)
    print(f"Consumer configured with group ID '{consumer_group_id}'.")

    consumer.subscribe([topic_name])
    print(f"Subscribed to topic '{topic_name}'. Waiting for messages...")

    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f'%% Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
            else:
                raise KafkaException(msg.error())
        else:
            print(f"\nMessage received successfully!")
            print(f"  Topic: {msg.topic()}")
            print(f"  Partition: {msg.partition()}")
            print(f"  Offset: {msg.offset()}")
            print(f"  Key: {msg.key().decode('utf-8') if msg.key() else 'None'}")
            print(f"  Value: {msg.value().decode('utf-8')}")

if __name__ == '__main__':
    main()

