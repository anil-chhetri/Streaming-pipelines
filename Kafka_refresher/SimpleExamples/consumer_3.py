""" consumer with 3 consumer id's. """

from confluent_kafka import Consumer, KafkaException
import sys
import json
import threading
import time

def create_consumer():
    # Consumer configuration
    conf = {
        'bootstrap.servers': 'kafka:9092',  # Kafka broker address
        'group.id': 'user_events_consumers',    # Consumer group ID
        'auto.offset.reset': 'earliest',        # Start from beginning if no offset
        'enable.auto.commit': True,             # Periodically commit offsets
        'auto.commit.interval.ms': 5000,        # Commit every 5 seconds
        # 'partition.assignment.strategy': 'roundrobin'  # Partition assignment strategy
    }

    # Create Consumer instance
    consumer = Consumer(conf)
    return consumer

def consume_messages(consumer_id):
    consumer = create_consumer()
    
    try:
        # Subscribe to topic
        consumer.subscribe(['user-events'], on_assign=on_assign)

        while True:
            # Poll for messages (timeout after 1 second)
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            
            # Process message
            print(f"Consumer {consumer_id} | "
                  f"Partition {msg.partition()} | "
                  f"Offset {msg.offset()} | "
                  f"Value: {json.loads(msg.value().decode('utf-8'))}")

    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        consumer.close()
        print(f"Consumer {consumer_id} closed")

def on_assign(consumer, partitions):
    print(f"Assigned partitions: {[p.partition for p in partitions]}")
    print(dir(consumer))

if __name__ == '__main__':
    threads = []
    for i in range(3):
        # Create a new thread for each consumer
        t = threading.Thread(target=consume_messages, args=(i,))
        t.daemon = True  # Mark as daemon so it doesn't prevent program exit
        t.start()  # Start the thread
        threads.append(t)
        print(f"Started consumer {i}")

    # Keep the main thread running to keep consumer threads alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")