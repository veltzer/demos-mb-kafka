package main

import (
	"fmt"
	"log"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

func main() {
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers": "localhost:29092",
		// "group.id":          "test-group",
		"auto.offset.reset": "earliest",
		// "fetch.max.wait.ms": 10,         // Reduce from 500ms to 10ms
		"fetch.min.bytes":   1,          // Don't wait to accumulate data
	})
	if err != nil {
		log.Fatal(err)
	}
	defer consumer.Close()

	consumer.Subscribe("test-topic", nil)

	for {
		msg, err := consumer.ReadMessage(-1)
		if err == nil {
			fmt.Printf("Message: %s\n", string(msg.Value))
		}
	}
}
