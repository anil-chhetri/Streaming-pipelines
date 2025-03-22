import json
import os
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer

# Kafka configuration
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'user-events')
MESSAGE_INTERVAL = float(os.environ.get('MESSAGE_INTERVAL', '500')) / 1000  # Convert to seconds

# Sample data
EVENT_TYPES = ['view', 'cart', 'purchase', 'remove_from_cart', 'wishlist']
CATEGORIES = ['electronics', 'clothing', 'home', 'books', 'beauty', 'sports', 'toys']
USER_IDS = [f'user_{i}' for i in range(1, 101)]  # 100 users
PRODUCT_IDS = [f'product_{i}' for i in range(1, 501)]  # 500 products

# Create Kafka producer
producer = None
max_retries = 10
retries = 0

print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")

while producer is None and retries < max_retries:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        print("Successfully connected to Kafka!")
    except Exception as e:
        retries += 1
        print(f"Failed to connect to Kafka (attempt {retries}/{max_retries}): {e}")
        time.sleep(5)

if producer is None:
    print("Failed to connect to Kafka after multiple attempts. Exiting.")
    exit(1)

def generate_event():
    """Generate a random user event"""
    now = datetime.now()
    event_time = (now - timedelta(seconds=random.randint(0, 60))).isoformat()
    event_type = random.choice(EVENT_TYPES)
    user_id = random.choice(USER_IDS)
    product_id = random.choice(PRODUCT_IDS)
    category = random.choice(CATEGORIES)
    price = round(random.uniform(5.0, 500.0), 2)
    quantity = random.randint(1, 5)
    
    return {
        "event_time": event_time,
        "event_type": event_type,
        "user_id": user_id,
        "product_id": product_id,
        "category": category,
        "price": price,
        "quantity": quantity
    }

def send_events():
    """Send events to Kafka topic"""
    events_sent = 0
    start_time = time.time()
    
    try:
        while True:
            event = generate_event()
            # Send event to Kafka
            producer.send(KAFKA_TOPIC, event)
            events_sent += 1
            
            # Print status every 100 events
            if events_sent % 100 == 0:
                elapsed = time.time() - start_time
                print(f"Sent {events_sent} events in {elapsed:.2f} seconds. "
                      f"Rate: {events_sent/elapsed:.2f} events/second")
            
            # Sleep for the interval
            time.sleep(MESSAGE_INTERVAL)
    except KeyboardInterrupt:
        print("Producer stopped by user")
    except Exception as e:
        print(f"Error in producing messages: {e}")
    finally:
        # Flush any remaining messages
        producer.flush()
        producer.close()
        print(f"Producer closed. Total events sent: {events_sent}")

if __name__ == "__main__":
    # Wait a few seconds for Kafka to be ready
    print("Waiting for Kafka to be ready...")
    time.sleep(10)
    print(f"Starting to send events to topic {KAFKA_TOPIC}...")
    send_events()