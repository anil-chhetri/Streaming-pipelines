# Apache Kafka: Components and Architecture

Apache Kafka is a distributed streaming platform designed for building real-time data pipelines and streaming applications. Let's explore its core components and how they work together to enable high-throughput, fault-tolerant, scalable data streaming.

## Key Components of Kafka

### **1. Borkers**:     
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



### **2. Topic**
A kafka topic is named stream or category where data is stored and organized. Thnk of it like a database table, a folder in filesytem or a channel in a messaging system. (eg. whatapp gorup fro specific purposes.)
Topic are logical channels or catagories to which message are published.  
topics enable the decoupling of data producer and consumers. producer publish data to topic and consuers subscribe to topics to read data.

- each topic has a unique name within a cluster.
- topics are  multi-subscriber - multiple consumres can read from single topic.
- topics are partitioned and replicated across borkers for scalability and fault tolerance.
- topics have a retention policy that determines how long messages are stored.
- topics can be compacted, meaning kafka keeps only the lsat value for each key.


##### **2. Key Components of a Kafka Topic**

##### **Partitions**
- **What**: A topic is divided into one or more partitions. Each partition is an ordered, immutable sequence of messages.
- **Why**: 
  - Scalability: Partitions allow Kafka to distribute data across multiple servers (brokers).
  - Parallelism: Consumers can read from different partitions simultaneously.
- **Example**: A topic with 3 partitions can handle 3x more throughput than a single partition.

##### **Offsets**
- **What**: A unique, incremental ID assigned to each message in a partition.
- **Why**: Offsets let consumers track their position in a partition (like a bookmark).

##### **Replication**
- **Replication Factor**: The number of copies of a partition (e.g., replication factor = 3 means 3 copies exist).
  - **Leader**: One broker handles all read/write requests for a partition.
  - **Followers**: Other brokers replicate the leader’s data for fault tolerance.

##### **Ordering Guarantees**
- Messages in a partition are ordered by offset. Across partitions, order is not guaranteed.


#### **Topic Configurations**
When creating a topic, specify these settings:
- **Number of Partitions**: Determines parallelism (e.g., 3 partitions = 3 consumers can read in parallel).
- **Replication Factor**: Ensures data durability (e.g., 2 replicas for basic fault tolerance).
- **Retention Policy**: 
  - Time-based (e.g., delete messages older than 7 days).
  - Size-based (e.g., delete old messages when the topic reaches 1 GB).
- **Log Compaction**: Keeps the latest value for each key (useful for stateful data).


### **3. partitions:** 

A partition is subdivision of a kafka topics, partitions are the unit of parallelism in kafka. each topic is split into one or more partitions. each partition is an ordered , immutable sequences of messages.

- **Key Properties**:
 - partiton allows horizontal scaling of message processing.
 - each partiton is an ordered, immutable sequences of messages.
 - a parition can only be consumed by one consumer within a consumer gorup at a time.
  - Messages in a partition are assigned a unique sequential ID called an **offset**.
  - Partitions allow Kafka to parallelize data storage and processing across multiple brokers and consumers.
  - Order is guaranteed **within a partition**, but not across partitions.
  - partition placement determins data distribution and load balancing across borkers.

#### **Why Use Partitions?**
1. **Scalability**:
   - Distribute data across brokers to handle high throughput (e.g., 100,000+ messages/sec).
2. **Parallelism**:
   - Multiple consumers can read from different partitions simultaneously (scaling consumer groups).
3. **Fault Tolerance**:
   - Each partition is replicated across brokers (replication factor ≥ 1). If a broker fails, replicas take over.


#### **Core Functions of Partitions**
##### **A. Data Distribution**
- **Producers** write messages to partitions using:
  - **Round-Robin** (no message key): Evenly distributes messages.
  - **Key-Based Hashing** (with message key): Same key → same partition (ensures order for related messages).

##### **B. Consumer Parallelism**
- **Consumer Groups**: Each consumer in a group reads from one or more partitions.
  - Maximum parallelism = number of partitions (e.g., 3 partitions → 3 consumers max).
  - If consumers > partitions, excess consumers idle.

##### **C. Replication**
- **Leader-Follower Model**:
  - Each partition has one **leader** (handles read/write) and N-1 **followers** (replicas).
  - Controlled by Kafka’s **controller** (elects leaders during failures).

##### **D. Ordered Processing**
- Messages in a partition are ordered by offset. Use keys to group related messages (e.g., user ID) for ordered processing.



#### **Summary**
- **Partitions** enable Kafka’s scalability, parallelism, and fault tolerance.
- **Design Tips**:
  - Choose partition count based on throughput and consumer needs.
  - Use keys for ordered processing.
  - Monitor partition health and consumer lag.



### **3. Producer**

producer publish data to topics of their choices. Think of it as a publicher that sends messages to kafka clusters. producer are decoupled from consumers (who read data), enabling scalable, real-time data streaming.

- **Key Properties**:

    - producer are client applications that sends records to kafka.
    - producer can choose which partition to send a record to (via a partition key or custom partitioner)
    - producer can operatre in synchronous or asynchronous mode
    - producer can set acknowledgement (acks) requirements for durability guarantees.
    - they include configurable batching, compression, and retry mechanisms.
    - producers can implement idempotence to prevent duplicate messages.


### **Core Functions of a Kafka Producer**

#### 1. **Configuration**
Configure connection properties, serializers, retries, and batching.

#### 2. **Message Creation**
Create messages with:
- **Value** (payload, required).
- **Key** (optional, used for partitioning).
- **Headers** (optional metadata).
- **Partition** (optional, override default partitioning).

#### 3. **Partitioning**
Decide which partition to send data to:
- **Key Hashing**: Messages with the same key go to the same partition.
- **Round Robin**: Distribute messages evenly if no key is provided.

#### 4. **Batching & Compression**
- **Batching**: Group messages to reduce network overhead.
- **Compression**: Compress data (e.g., `gzip`, `snappy`) to save bandwidth.

#### 5. **Error Handling & Retries**
- Retry failed messages (e.g., broker failures).
- Handle errors like timeouts or invalid topics.

#### 6. **Serialization**
Convert data to bytes for transmission (e.g., JSON, Avro).

#### 7. **Delivery Acknowledgements**
Control reliability via `acks`:
- `acks=0`: No acknowledgment (fast, unreliable).
- `acks=1`: Leader acknowledgment (default).
- `acks=all`: All replicas acknowledgment (most reliable).

#### 8. **Async vs Sync Production**
- **Async**: Non-blocking (higher throughput).
- **Sync**: Block until the message is sent (slower, more reliable).


### **5 . Consumers**

consumers read data from kafka topics.



- **Key Properties**:

    - consumer subscribe to one or more topics.
    - consumres maintain their position in each partition
    - consumers can read from the beginning of a topics or from the latest message
    - they can commit offsets automatically or manually
    - consumers can be statically or dynamically assigned partitions
    - consumer instance with the same grop id form a consumre group for parallel processing.