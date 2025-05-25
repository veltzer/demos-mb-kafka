package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/IBM/sarama"
)

type KafkaClient struct {
	client sarama.Client
	admin  sarama.ClusterAdmin
}

// NewKafkaClient creates a new Kafka client
func NewKafkaClient(brokers []string) (*KafkaClient, error) {
	config := sarama.NewConfig()
	config.Version = sarama.V2_8_0_0 // Use appropriate Kafka version
	config.Consumer.Return.Errors = true

	// Create client
	client, err := sarama.NewClient(brokers, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kafka client: %w", err)
	}

	// Create admin client
	admin, err := sarama.NewClusterAdminFromClient(client)
	if err != nil {
		client.Close()
		return nil, fmt.Errorf("failed to create Kafka admin client: %w", err)
	}

	return &KafkaClient{
		client: client,
		admin:  admin,
	}, nil
}

// Close closes the Kafka client connections
func (kc *KafkaClient) Close() error {
	if kc.admin != nil {
		kc.admin.Close()
	}
	if kc.client != nil {
		return kc.client.Close()
	}
	return nil
}

// ListTopics retrieves all topics from the Kafka cluster
func (kc *KafkaClient) ListTopics() (map[string]sarama.TopicDetail, error) {
	topics, err := kc.admin.ListTopics()
	if err != nil {
		return nil, fmt.Errorf("failed to list topics: %w", err)
	}
	return topics, nil
}

// GetTopicMetadata gets detailed metadata for a specific topic
func (kc *KafkaClient) GetTopicMetadata(topicName string) (*sarama.TopicMetadata, error) {
	req := &sarama.MetadataRequest{
		Topics: []string{topicName},
	}

	brokers := kc.client.Brokers()
	if len(brokers) == 0 {
		return nil, fmt.Errorf("no brokers available")
	}

	response, err := brokers[0].GetMetadata(req)
	if err != nil {
		return nil, fmt.Errorf("failed to get topic metadata: %w", err)
	}

	for _, topic := range response.Topics {
		if topic.Name == topicName {
			return topic, nil
		}
	}

	return nil, fmt.Errorf("topic %s not found", topicName)
}

// GetBrokerInfo gets information about all brokers
func (kc *KafkaClient) GetBrokerInfo() []*sarama.Broker {
	return kc.client.Brokers()
}

// GetConsumerGroups lists all consumer groups
func (kc *KafkaClient) GetConsumerGroups() (map[string]string, error) {
	groups, err := kc.admin.ListConsumerGroups()
	if err != nil {
		return nil, fmt.Errorf("failed to list consumer groups: %w", err)
	}
	return groups, nil
}

func printUsage() {
	fmt.Printf("Usage: %s [broker1:port[,broker2:port,...]] [options]\n", os.Args[0])
	fmt.Println()
	fmt.Println("If no broker address is provided, defaults to localhost:29092")
	fmt.Println()
	fmt.Println("Options:")
	fmt.Println("  --detailed    Show detailed topic information")
	fmt.Println("  --brokers     Show broker information")
	fmt.Println("  --groups      Show consumer groups")
	fmt.Println("  --help        Show this help message")
	fmt.Println()
	fmt.Println("Examples:")
	fmt.Printf("  %s                                 # Use default localhost:29092\n", os.Args[0])
	fmt.Printf("  %s --detailed                      # Use default with detailed info\n", os.Args[0])
	fmt.Printf("  %s localhost:9092                  # Specify broker\n", os.Args[0])
	fmt.Printf("  %s localhost:29092 --detailed      # Specify broker with options\n", os.Args[0])
	fmt.Printf("  %s broker1:9092,broker2:9092       # Multiple brokers\n", os.Args[0])
}

func main() {
	var brokerString string
	var showDetailed, showBrokers, showGroups bool

	// Parse command line arguments
	if len(os.Args) == 1 {
		// No arguments, use default
		brokerString = "localhost:29092"
	} else {
		// Check if first argument is an option or broker address
		firstArg := os.Args[1]
		if strings.HasPrefix(firstArg, "--") {
			// First argument is an option, use default broker
			brokerString = "localhost:29092"
			// Parse all arguments as options
			for i := 1; i < len(os.Args); i++ {
				switch os.Args[i] {
				case "--detailed":
					showDetailed = true
				case "--brokers":
					showBrokers = true
				case "--groups":
					showGroups = true
				case "--help":
					printUsage()
					os.Exit(0)
				default:
					fmt.Printf("Unknown option: %s\n", os.Args[i])
					printUsage()
					os.Exit(1)
				}
			}
		} else {
			// First argument is broker address
			brokerString = firstArg
			// Parse remaining arguments as options
			for i := 2; i < len(os.Args); i++ {
				switch os.Args[i] {
				case "--detailed":
					showDetailed = true
				case "--brokers":
					showBrokers = true
				case "--groups":
					showGroups = true
				case "--help":
					printUsage()
					os.Exit(0)
				default:
					fmt.Printf("Unknown option: %s\n", os.Args[i])
					printUsage()
					os.Exit(1)
				}
			}
		}
	}

	// Parse broker addresses
	brokers := strings.Split(brokerString, ",")

	// Create Kafka client
	kafkaClient, err := NewKafkaClient(brokers)
	if err != nil {
		log.Fatalf("Failed to create Kafka client: %v", err)
	}
	defer kafkaClient.Close()

	fmt.Printf("Connected to Kafka cluster: %s\n", brokerString)
	fmt.Println(strings.Repeat("=", 60))

	// Show broker information if requested
	if showBrokers {
		fmt.Println("\n📡 BROKER INFORMATION:")
		fmt.Println(strings.Repeat("-", 40))
		brokers := kafkaClient.GetBrokerInfo()
		for _, broker := range brokers {
			fmt.Printf("Broker ID: %d\n", broker.ID())
			fmt.Printf("Address: %s\n", broker.Addr())
			// fmt.Printf("Connected: %t\n", broker.Connected())
			fmt.Println()
		}
	}

	// List and display topics
	fmt.Println("\n📋 TOPICS:")
	fmt.Println(strings.Repeat("-", 40))

	topics, err := kafkaClient.ListTopics()
	if err != nil {
		log.Fatalf("Failed to list topics: %v", err)
	}

	if len(topics) == 0 {
		fmt.Println("No topics found.")
	} else {
		for topicName, topicDetail := range topics {
			fmt.Printf("📁 Topic: %s\n", topicName)
			
			if showDetailed {
				fmt.Printf("   Partitions: %d\n", topicDetail.NumPartitions)
				fmt.Printf("   Replication Factor: %d\n", topicDetail.ReplicationFactor)
				
				// Get additional metadata
				metadata, err := kafkaClient.GetTopicMetadata(topicName)
				if err == nil {
					if metadata.Err != sarama.ErrNoError {
						fmt.Printf("   Error: %s\n", metadata.Err.Error())
					}
					fmt.Printf("   Partition Details:\n")
					for _, partition := range metadata.Partitions {
						fmt.Printf("     Partition %d: Leader=%d, Replicas=%v, ISR=%v\n",
							partition.ID, partition.Leader, partition.Replicas, partition.Isr)
					}
				}
				
				// Show topic configuration if available
				if len(topicDetail.ConfigEntries) > 0 {
					fmt.Printf("   Configuration:\n")
					for key, value := range topicDetail.ConfigEntries {
						if value != nil {
							fmt.Printf("     %s: %s\n", key, *value)
						}
					}
				}
			} else {
				fmt.Printf("   Partitions: %d, Replication Factor: %d\n", 
					topicDetail.NumPartitions, topicDetail.ReplicationFactor)
			}
			fmt.Println()
		}
	}

	// Show consumer groups if requested
	if showGroups {
		fmt.Println("\n👥 CONSUMER GROUPS:")
		fmt.Println(strings.Repeat("-", 40))
		groups, err := kafkaClient.GetConsumerGroups()
		if err != nil {
			fmt.Printf("Failed to list consumer groups: %v\n", err)
		} else if len(groups) == 0 {
			fmt.Println("No consumer groups found.")
		} else {
			for groupID, protocol := range groups {
				fmt.Printf("Group: %s (Protocol: %s)\n", groupID, protocol)
			}
		}
	}

	fmt.Printf("\nTotal topics: %d\n", len(topics))
}
