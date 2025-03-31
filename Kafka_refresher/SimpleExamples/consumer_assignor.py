import json
import threading
import time

from confluent_kafka import Consumer, KafkaException, TopicPartition



EVENT_TOPIC_NAME = 'user-events'
KAFKA_BROKER = 'kafka:9092'


def on_assign(consumer, paritions):
    print(f'Assigned paritions: {[p.partition for p in paritions]}')
    # print('reading for the begining of the topic.\n')

    # for partition in paritions:
    #     partition.offset = -2

    # consumer.assign(paritions)



def create_consumer(consumer_id, parition_assignor):

    parition_assignor = parition_assignor or None

    if parition_assignor not in ['range', 'roundrobin', 'cooperative-sticky']:
        parition_assignor = 'range'

    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'user_events_consumers',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 5000,
        'partition.assignment.strategy': parition_assignor
    }

    consumer = Consumer(conf)

    try: 
        # starting consuming
        consumer.subscribe([EVENT_TOPIC_NAME], on_assign=on_assign)

        while True:

            msg = consumer.poll(4)

            if msg is None:
                # print('No message returned from poll')
                continue
            
            if msg.error():
                raise KafkaException(msg.error())

            # Process message
            print(f"Consumer {consumer_id} | "
                f"Partition {msg.partition()} | "
                f"Offset {msg.offset()} | "
                f"Value: {json.loads(msg.value().decode('utf-8'))}")

    except KeyboardInterrupt:
        print('shutting down consumer function. {consumer_id}')
        pass

    finally:
        consumer.close()
        print(f"Consumer {consumer_id} closed")


if __name__ == '__main__':
    threads = []

    for i in range(3):

        t = threading.Thread(target=create_consumer, args=(i,'cooperative-sticky',))
        t.daemon = True
        t.start()
        threads.append(t)
        print(f'Started consumer {i}')

    try:
        while True:
            time.sleep(2)
            # print('Main method is sleept for 2 second.')
    except KeyboardInterrupt:
        print('shutting down main function.')
    
