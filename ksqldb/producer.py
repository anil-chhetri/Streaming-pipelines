from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField 

from faker import Faker

import random

def generate_events():
    return {
        "event_type": "user_signup",
        "user_id": random.randint(10000, 99999),
        "timestamp": Faker().unix_time(),
        "event_data": {
            "username": Faker().user_name(),
            "email": Faker().email(),
            "signup_method": random.choice(["email", "google", "facebook"]),
            "signup_timestamp": Faker().unix_time(),
            "location": {
                "city": Faker().city(),
                "state": Faker().state(),
                "country": Faker().country()
            }
        }
    }


def create_topic(topic_name):
    admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})
    topic_metadata = admin_client.list_topics(timeout=10)

    if topic_name not in topic_metadata.topics:
        topic = NewTopic(topic_name, num_partitions=5, replication_factor=1)
        f = admin_client.create_topics([topic])
        for topic, f in f.items():
            try:
                f.result()
                print(f"Topic {topic_name} created.")
            except Exception as e:
                print(f"Failed to create topic {topic_name}: {e}")
    else:
        print(f"Topic {topic_name} already exists.")


def produce_event_to_kafka():
    try:
        producer = Producer({
            "bootstrap.servers": "localhost:9092",
            "linger.ms": 5000,
        })
        event = generate_events()
        key_context = SerializationContext("user_signups", MessageField.KEY)
        value_context = SerializationContext("user_signups", MessageField.VALUE)
        producer.produce("user_signups", key=StringSerializer()(str(event['user_id']), ctx=key_context), value=StringSerializer()(str(event), ctx=value_context))
        producer.poll(5)
    except Exception as e:
        print(f"Error producing event: {e}")
    finally:
        producer.flush()
    
    print(f"Produced event: {event}")


if __name__ == "__main__":
    create_topic("user_signups")
    for _ in range(2):
        produce_event_to_kafka()
    print("Finished producing events.")