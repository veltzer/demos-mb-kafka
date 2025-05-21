#!/usr/bin/env python

"""
Create a topic in Kafka
"""

import sys
from confluent_kafka.admin import AdminClient, NewTopic


def create_kafka_topic(bootstrap_servers,
                       topic_name, num_parts=1, replication_factor=1):
    """
    Create a Kafka topic with the specified configuration using
    confluent-kafka.

    Args:
        bootstrap_servers (str): Comma-separated list of broker
        addresses (host:port)
        topic_name (str): Name of the topic to create
        num_parts (int): Number of partitions for the topic
        replication_factor (int): Replication factor for the topic
    """
    # Configure the client
    conf = {'bootstrap.servers': bootstrap_servers}

    # Create an Admin client
    admin_client = AdminClient(conf)

    # Create topic configuration
    topic = NewTopic(
        topic_name,
        num_parts=num_parts,
        replication_factor=replication_factor
    )

    # Create the topic (returns a dict of <topic, future> entries)
    futures = admin_client.create_topics([topic])

    # Wait for operation to complete
    for topic_name_f, future in futures.items():
        future.result()  # None if the topic creation was successful
        print(f"Successfully created topic: {topic_name_f}")
        print(f"Partitions: {num_parts}, Rep Factor: {replication_factor}")


def main():
    # Default values
    bootstrap_servers = "localhost:29092"  # Use the external port we mapped

    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} <name> [parts] [rep_factor]")
        sys.exit(1)

    topic_name = sys.argv[1]
    num_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    factor = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    create_kafka_topic(bootstrap_servers, topic_name, num_parts, factor)


if __name__ == "__main__":
    main()
