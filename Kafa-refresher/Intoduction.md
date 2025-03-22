# Apache Kafka: Components and Architecture

Apache Kafka is a distributed streaming platform designed for building real-time data pipelines and streaming applications. Let's explore its core components and how they work together to enable high-throughput, fault-tolerant, scalable data streaming.

## Key Components of Kafka

1. Borkers:     
Broker in Apache Kafka is a server responsible for storing data, handling client requests, and managing communication between producers (data publishers) and consumers (data subscribers). Think of it as a node in a Kafka cluster that ensures data is reliably stored, replicated, and distributed. It is the heart of kafka cluster. They are servers that stored published messages and serve client requests.

Things to know about borker: 
- Each broker is identifies by a unique integer ID.
- Broker manage pratitions for topic distributed across the cluster
- a single broker can handle thousands of partitions and millions of messages per second.
- Broker coordinate with Zookeeper or KRaft to maintain cluster state.
- Broker handle client connections and respond to produce/consume requests.
- They mange data replication between nodes for fault tolerance.

Key Functions of a Kafka Broker
- Message Storage  
Brokers store messages in topics, which are divided into partitions (ordered, immutable sequences of records).  
Each partition is a log file on the broker’s disk (e.g., /tmp/kafka-logs).    
Messages are retained based on time (e.g., 7 days) or size (e.g., 1 GB) policies.

- Request Handling
Producers write messages to the leader partition of a topic.  
Consumers read messages from partitions, tracking their position via offsets.  
Brokers handle both requests efficiently using high-throughput, low-latency I/O.  
- Replication and fault tolerance
Each partition has replicas across multiple brokers (e.g., replication factor = 3).  
One replica is the leader (handles read/write); others are followers (replicate data).  
If a leader fails, brokers elect a new leader automatically.  
- Offset Management
Brokers track consumer progress via offsets stored in the __consumer_offsets topic.  
Consumers can start reading from the earliest (--from-beginning) or latest offset.   
- Cluster Coordination
Brokers use Zookeeper (or KRaft in newer versions) to:   
Elect a controller (manages partition states).
Sync metadata (e.g., topic configurations, broker health).  
Detect broker failures.
- Log Retention and compaction.
Delete old messages with log.retention.hours or retain the latest value per key via log compaction.
