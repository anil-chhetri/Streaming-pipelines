from Customer import Customer

import logging
import json
import time 

from confluent_kafka import Producer, KafkaError
from confluent_kafka.admin import NewTopic, AdminClient



logging.basicConfig(level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class KafkaProducer:

    KAFKA_BROKER = 'kafka:9092'
    KAFKA_PRODUCER_DEFAULT_CONFIG = {
        'bootstrap.servers': KAFKA_BROKER,
        'client.id': 'customer-producer',
        'acks': 'all',
        'retries': 5,
        'retry.backoff.ms': 5000, 
        'linger.ms': 5,
        'compression.type': 'snappy',
        'queue.buffering.max.messages': 1000,
    }

    def __init__(self, config= {}):
        self.logger = logging.getLogger(__name__)
        self.producer = Producer(
            {**KafkaProducer.KAFKA_PRODUCER_DEFAULT_CONFIG
             , **config}
        )

    def create_topic(self, name=''):
        config = {
            "bootstrap.servers": KafkaProducer.KAFKA_BROKER
        }
        admin_client = AdminClient(config)

        topics = admin_client.list_topics().topics.keys()
        self.logger.info(topics)

        if name in topics:
            self.logger.info('topics is already created.')
            return None
            
        topic_list = [
            NewTopic(name,num_partitions=6,replication_factor=1)
        ]
        result = admin_client.create_topics(topic_list)
        for topic, future_function in result.items():
            try:
                future_function.result()
                self.logger.info(dir(future_function))
                self.logger.info(f'Topic created: {topic}')
            except Exception as e:
                logger.info(e)
                logger.info('topic creation failed.')

    def start(self, topic_name = 'customer_event_topic', event_producing_object=None):
        event = event_producing_object().as_dict()
        self.producer.produce(
            topic_name,
            key = str(event.get('id')).encode('utf-8'),
            value = json.dumps(event).encode('utf-8'),
            on_delivery=self.delivery_report
        )
        num = self.producer.poll(5)
        self.logger.info(f"number of message sent: {num}")


    def delivery_report(self, error, msgs):
        if error is not None:
            logger.info(f'message not delivered: {error}, {msgs.value()}')

        logger.info(f'messaged delived to {msgs.topic()}[{msgs.partition()}]')

    def stop(self):
        self.producer.flush(10)




def main(logger):
    logger.info('starting producer.')
    customer = Customer.get_customer()
    logger.info(customer.as_dict())

    producer = KafkaProducer()
    producer.create_topic('customer_event_topic')
    try:
        while True:
            producer.start('customer_event_topic', Customer.get_customer)
            time.sleep(10)
            
    except KeyboardInterrupt as k:
        logger.info('stopping producer')
        producer.stop()
    except Exception as e:
        producer.stop()
        print(e)
        logger.info(f'error in kafka: {e}')




if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    main(logger)