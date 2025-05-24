package main

import (
	"log"
	"github.com/confluentinc/confluent-kafka-go/kafka"
)

func main() {
	producer, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": "localhost:29092",
	})
	if err != nil {
		log.Fatal(err)
	}
	defer producer.Close()

	producer.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{Topic: &[]string{"test-topic"}[0], Partition: kafka.PartitionAny},
		Value:          []byte("Hello Kafka!"),
	}, nil)
	producer.Flush(1000)
}
