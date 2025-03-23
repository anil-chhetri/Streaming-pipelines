from faker import Faker
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

import logging
import json
import time
import random
from datetime import datetime


logging.basicConfig(level=logging.INFO
                    , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#kafka configurations
KAFKA_BROKER = 'kafka:9092'
USER_EVENTS_TOPIC = 'user-events'
PROCESSED_EVENTS_TOPIC = 'processed-events'
HIGH_VALUE_EVENTS_TOPIC = 'high-value-events'

fake = Faker()

def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def create_topics():
    """Creates required Kafka topics if they don't exists."""
    config = {
        "bootstrap.servers": KAFKA_BROKER
    }
    admin_client = AdminClient(config)
    
    topic_list = [
        NewTopic(USER_EVENTS_TOPIC, num_partitions=3, replication_factor=1)
    ]

    fs = admin_client.create_topics(topic_list)

    # wait for operation to complete
    for topic, f in fs.items():
        try:
            f.result()
            logger.info(f"Topic {topic} created.")
        except Exception as e:
            logger.info(f"Topic {topic} creation failed.")
            logger.info(e)
            pass


class UserEventProducer:
    """Simulates user activity events and publishes them to kafka"""
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BROKER,
            'client.id': 'user-event-producer',
            'acks': 'all',                    # Wait for all replicas to acknowledge
            'retries': 5,                     # Retry on temporary failures
            'retry.backoff.ms': 500,          # Backoff time between retries
            'batch.size': 16384,              # Batch size in bytes
            'linger.ms': 5,                   # Wait time to accumulate messages
            'compression.type': 'snappy',     # Compress messages
            'queue.buffering.max.messages': 10000,

        })
        self.running = False
        self.event_types = ['login', 'logout', 'purchase', 'page_view', 'add_to_cart']
        self.event_values = {
            'login': 5,
            'logout': 1,
            'purchase': 50,
            'page_view': 1,
            'add_to_cart': 10
        }

    def generate_event(self):
        """Generate a random user event."""
        user_id = random.randint(1, 100)
        event_type = random.choice(self.event_types)
        event_value = self.event_values[event_type]
        
        # Add some randomization to purchase values
        if event_type == 'purchase':
            event_value = random.randint(10, 500)
        
        return {
            'user_id': user_id,
            'event_type': event_type,
            'event_value': event_value,
            'timestamp': datetime.now().isoformat(),
            'device': random.choice(['mobile', 'desktop', 'tablet']),
            'location': fake.city()
        }
    
    def start(self, interval=1.0):
        """Start producing events at the specified interval."""
        self.running = True
        
        def produce_events():
            while self.running:
                try:
                    # Generate and publish event
                    event = self.generate_event()
                    
                    # Use user_id as the key for partitioning (ensures events from
                    # the same user go to the same partition)
                    key = str(event['user_id']).encode('utf-8')
                    
                    # Convert event to JSON and encode
                    event_json = json.dumps(event).encode('utf-8')
                    
                    # Produce message with callback
                    self.producer.produce(
                        USER_EVENTS_TOPIC,
                        key=key,
                        value=event_json,
                        callback=delivery_report
                    )
                    
                    # Serve delivery callbacks
                    self.producer.poll(0)

                    self.producer.flush()
                    
                    logger.info(f"Produced event: {event}")
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error producing event: {e}")
                    time.sleep(1)
        
        # Start producer thread
        logger.info("Producer started")
        produce_events()

    def stop(self):
        """Stop the producer."""
        self.running = False
        
        # Flush any pending messages
        remaining = self.producer.flush(timeout=10)
        if remaining > 0:
            logger.warning(f"{remaining} messages were not delivered")


def main():
    logger.info('Starting kafka producer')

    time.sleep(10)

    logger.info('creating topic started.')
    create_topics()

    try: 

        producer = UserEventProducer()
        producer.start(interval=10)

        while True:
            logger.info("Inside this while loop")
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info('shutting down')
    finally:
        producer.stop()
        logger.info('commplete')

if __name__== "__main__":
    main()
