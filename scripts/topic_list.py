#!/usr/bin/env python

"""
List all topics in a kafka server
"""

import sys
from confluent_kafka.admin import AdminClient


def list_kafka_topics(bootstrap_servers):
    """
    List all Kafka topics.

    Args:
        bootstrap_servers (str):
        Comma-separated list of broker addresses (host:port)
    """
    # Configure the client
    conf = {'bootstrap.servers': bootstrap_servers}

    # Create an Admin client
    admin_client = AdminClient(conf)

    # Get cluster metadata
    metadata = admin_client.list_topics(timeout=10)

    print("Available Kafka Topics:")
    print("-" * 40)

    if not metadata.topics:
        print("No topics found.")
        return

    # Sort topics alphabetically for better readability
    sorted_topics = sorted(metadata.topics.keys())

    for topic_name in sorted_topics:
        topic_metadata = metadata.topics[topic_name]
        partition_count = len(topic_metadata.partitions)

        print(f"Topic: {topic_name}")
        print(f"  Partitions: {partition_count}")

        # Show partition details
        for part_id, part in topic_metadata.partitions.items():
            reps = len(part.replicas)
            print(f"    Part {part_id}: Leader={part.leader}, Reps={reps}")


def list_topics_simple(bootstrap_servers):
    """
    List all Kafka topics in a simple format (just topic names).

    Args:
        bootstrap_servers (str):
        Comma-separated list of broker addresses (host:port)
    """
    # Configure the client
    conf = {'bootstrap.servers': bootstrap_servers}

    # Create an Admin client
    admin_client = AdminClient(conf)

    # Get cluster metadata
    metadata = admin_client.list_topics(timeout=10)

    if not metadata.topics:
        print("No topics found.")
        return

    print("Kafka Topics:")
    for topic_name in sorted(metadata.topics.keys()):
        print(f"  - {topic_name}")


def main():
    # Default values
    bootstrap_servers = "localhost:29092"  # Use the external port we mapped

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--simple" or sys.argv[1] == "-s":
            list_topics_simple(bootstrap_servers)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage: python list_topics.py [--simple|-s] [--help|-h]")
            print("  --simple, -s: Show only topic names")
            print("  --help, -h: Show this help message")
            sys.exit(0)
        else:
            print("Unknown argument. Use --help for usage information.")
            sys.exit(1)
    else:
        list_kafka_topics(bootstrap_servers)


if __name__ == "__main__":
    main()
