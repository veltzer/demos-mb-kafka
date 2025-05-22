package main

import (
	"fmt"
	"log"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

func main() {
	// Create admin client
	adminClient, err := kafka.NewAdminClient(&kafka.ConfigMap{
		"bootstrap.servers": "localhost:29092",
		"client.id":         "kafka-version-checker",
	})
	if err != nil {
		log.Fatalf("Failed to create admin client: %v", err)
	}
	defer adminClient.Close()

	// Get metadata
	metadata, err := adminClient.GetMetadata(nil, false, 10000)
	if err != nil {
		log.Fatalf("Failed to get metadata: %v", err)
	}

	// Print basic cluster information
	fmt.Printf("Connected to Kafka cluster\n")
	fmt.Printf("Number of Brokers: %d\n", len(metadata.Brokers))
	fmt.Printf("Number of Topics: %d\n", len(metadata.Topics))
	
	// Print broker information
	for _, broker := range metadata.Brokers {
		fmt.Printf("Broker ID: %d, Address: %s:%d\n", 
			broker.ID, broker.Host, broker.Port)
	}
}
