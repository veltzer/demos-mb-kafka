#!/usr/bin/env python

"""
Delete a topic on a Kafka server
"""

import sys
from confluent_kafka.admin import AdminClient


def delete_kafka_topic(bootstrap_servers, topic_name, force=False):
    """
    Delete a Kafka topic by name.

    Args:
        bootstrap_servers (str):
        Comma-separated list of broker addresses (host:port)
        topic_name (str): Name of the topic to delete
        force (bool): If True, skip confirmation prompt
    """
    # Configure the client
    conf = {'bootstrap.servers': bootstrap_servers}

    # Create an Admin client
    admin_client = AdminClient(conf)

    # First, check if the topic exists
    metadata = admin_client.list_topics(timeout=10)

    if topic_name not in metadata.topics:
        print(f"Topic '{topic_name}' does not exist.")
        return False

    # Show topic info before deletion
    topic_metadata = metadata.topics[topic_name]
    partition_count = len(topic_metadata.partitions)
    print(f"Found topic: {topic_name}")
    print(f"Partitions: {partition_count}")

    # Confirmation prompt (unless forced)
    if not force:
        response = input(f"delete topic '{topic_name}'? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Topic deletion cancelled.")
            return False

    # Delete the topic
    futures = admin_client.delete_topics([topic_name], operation_timeout=30)

    # Wait for operation to complete
    for topic, future in futures.items():
        future.result()  # The result will be None if deletion was successful
        print(f"Successfully deleted topic: {topic}")
        return True


def list_available_topics(bootstrap_servers):
    """
    Helper function to list available topics.

    Args:
        bootstrap_servers (str):
        Comma-separated list of broker addresses (host:port)
    """
    conf = {'bootstrap.servers': bootstrap_servers}
    admin_client = AdminClient(conf)
    metadata = admin_client.list_topics(timeout=10)

    if not metadata.topics:
        print("No topics available.")
        return

    print("Available topics:")
    for topic_name in sorted(metadata.topics.keys()):
        print(f"  - {topic_name}")


def main():
    # Default values
    bootstrap_servers = "localhost:29092"  # Use the external port we mapped

    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} <name> [--force|-f] [--list|-l] [--help|-h]")
        print("\nOptions:")
        print("  --force, -f: Delete without confirmation prompt")
        print("  --list, -l: List available topics")
        print("  --help, -h: Show this help message")
        print("\nExamples:")
        print("  python delete_topic.py my_topic")
        print("  python delete_topic.py my_topic --force")
        print("  python delete_topic.py --list")
        sys.exit(1)

    # Parse arguments
    if sys.argv[1] == "--list" or sys.argv[1] == "-l":
        list_available_topics(bootstrap_servers)
        sys.exit(0)
    elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print(f"{sys.argv[0]} <name> [--force|-f] [--list|-l] [--help|-h]")
        print("\nOptions:")
        print("  --force, -f: Delete without confirmation prompt")
        print("  --list, -l: List available topics")
        print("  --help, -h: Show this help message")
        print("\nExamples:")
        print("  python delete_topic.py my_topic")
        print("  python delete_topic.py my_topic --force")
        print("  python delete_topic.py --list")
        sys.exit(0)

    topic_name = sys.argv[1]
    force = False

    # Check for force flag
    if len(sys.argv) > 2:
        if sys.argv[2] == "--force" or sys.argv[2] == "-f":
            force = True
        else:
            print(f"Unknown argument: {sys.argv[2]}")
            print("Use --help for usage information.")
            sys.exit(1)

    # Delete the topic
    success = delete_kafka_topic(bootstrap_servers, topic_name, force)

    if success:
        print(f"Topic '{topic_name}' has been successfully deleted.")
    else:
        print(f"Failed to delete topic '{topic_name}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
