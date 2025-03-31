from Customer import Customer

import logging
import time 
import json
from deepdiff import DeepDiff

from confluent_kafka import SerializingProducer
from confluent_kafka.admin import NewTopic, AdminClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema



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
    SCHEMA_REISTRY_URL = 'http://schema-registry:8081'
    KAFKA_TOPIC = 'customer_event_topic'

    def __init__(self, config= {}):
        self.logger = logging.getLogger(__name__)
        config = {
                **KafkaProducer.KAFKA_PRODUCER_DEFAULT_CONFIG
                , **config
            }
        self.producer = self.create_producer(config)


    def create_producer(self, config):
        producer = SerializingProducer(config)
        return producer

    @classmethod
    def register_schema_registry(cls, subject_name, path_to_arvo='schema/v1_customer_schema.avsc'):
        try:
            config = {
                'url': KafkaProducer.SCHEMA_REISTRY_URL
            }

            schema_client = SchemaRegistryClient(conf=config)

            with open(path_to_arvo) as f:
                schema_str = f.read()

            schema_id = schema_client.register_schema(subject_name, Schema(schema_str, schema_type="AVRO"))
            logger.info(f'schema registered: {subject_name} with schema id: {schema_id}')

            avro = AvroSerializer(
                schema_registry_client=schema_client,
                schema_str=schema_str
            )

        except Exception as e:
            logger.info(f'error in registering schema: {e}')
            avro = None

        return avro
    
    @classmethod
    def update_schema_registry(cls, path_to_arvo, subject_name=None, compatibility='FULL'):
        subject_name = subject_name or KafkaProducer.KAFKA_TOPIC + '-value'
        config = {
            'url': KafkaProducer.SCHEMA_REISTRY_URL
        }

        schema_client = SchemaRegistryClient(conf=config)

        with open(path_to_arvo) as f:
            schema_str = f.read()

        try:
            latest_schema = schema_client.get_latest_version(subject_name)
            logger.info(f'latest schema version: {latest_schema.version}')
            # print(dir(latest_schema))
            
            latest_schema_str = dict(json.loads(latest_schema.schema.schema_str))
            current_schema_str = dict(json.loads(schema_str))

            print(latest_schema_str)
            print(current_schema_str)

            diff_result = DeepDiff(latest_schema_str, current_schema_str, ignore_order=True)
            logger.info(bool(diff_result))

            if diff_result: # true: diff result is empty
                logger.info('schema is different')

                logger.info('changing schema compatibility')
                schema_client.set_compatibility(subject_name, compatibility)

                logger.info('testing compatibility of schema')
                result = schema_client.test_compatibility(subject_name, Schema(schema_str, schema_type="AVRO"), version='latest')
                if not result:
                    logger.info('schema is not compatible')
                else: 
                    logger.info('schema is compatible')
            else: 
                logger.info('schema is same')

        except Exception as e:
            logger.info(f'error in updating schema registry: {e}')
        
        return KafkaProducer.register_schema_registry(subject_name, path_to_arvo)

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
                self.logger.info(f'Topic created: {topic}')
            except Exception as e:
                logger.info(e)
                logger.info('topic creation failed.')

    def start(self, topic_name = 'customer_event_topic', event_producing_object=None):
        event = event_producing_object().as_dict()
        self.producer.produce(
            topic_name,
            key = str(event.get('id')),
            value = event,
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


    avro_config = {
        "key.serializer": StringSerializer(),
        "value.serializer": KafkaProducer.update_schema_registry(path_to_arvo='schema/v2_customer_schema.avsc')
    }
    producer = KafkaProducer(avro_config)
    producer.create_topic(KafkaProducer.KAFKA_TOPIC)
    try:
        while True:
            producer.start(KafkaProducer.KAFKA_TOPIC, Customer.get_customer)
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