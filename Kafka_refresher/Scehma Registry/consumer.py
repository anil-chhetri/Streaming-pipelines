import logging
import time

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer



logging.basicConfig(level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class KafkaConsumer():

    SCHEMA_REISTRY_URL = 'http://schema-registry:8081'
    KAFKA_BROKER = 'kafka:9092'
    CONSUMER_CONFIG = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'customer-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 5000,
        'max.poll.interval.ms': 300000
    }
    KAFAK_TOPIC = "customer_event_topic"

    def __init__(self, other_config):
        self.logger = logging.getLogger(__name__)
        config = {
            **KafkaConsumer.CONSUMER_CONFIG,
            **other_config
        }
        self.consumer = self.create_consumer(config)

    def create_consumer(self, config):
        consumer = DeserializingConsumer(config)
        consumer.subscribe([KafkaConsumer.KAFAK_TOPIC], on_assign=self.on_assign_callback)
        return consumer
    
    @classmethod
    def get_register_schema_registry(cls):
        config = {
            'url': KafkaConsumer.SCHEMA_REISTRY_URL
        }

        schema_client = SchemaRegistryClient(conf=config)
        logger.info('registering schema to schema registry')

        with open('schema/v1_customer_schema.avsc') as f:
            schema_str = f.read()

        avro = AvroDeserializer(
            schema_registry_client=schema_client,
            schema_str=schema_str
        )

        return avro

    def on_assign_callback(self, consumer, partitions):
        self.logger.info(f"partitions assigned: {partitions}")

    
    def start_consuming(self, time_out = 10):
        msg = self.consumer.poll(time_out)

        if msg is None:
            self.logger.info("No message found.")
            return None

        if msg.error():
            self.logger.info(f'Consumer error: {msg.error}')
            return None
        
        print('consumed message')
        print(f"  Key: {msg.key()}")
        print(f"  Value: {msg.value()}")
        print(f"  Timestamp: {msg.timestamp()[1]}")
        print(f"  Partition: {msg.partition()}, Offset: {msg.offset()}")
        print("-" * 50)

    def stop(self):
        self.consumer.close()

def main(logger):

    arvo_config = {
        "key.deserializer": StringDeserializer(),
        "value.deserializer": KafkaConsumer.get_register_schema_registry()
    }

    consumer = KafkaConsumer(arvo_config)
    try:
        while True:
            msgs = consumer.start_consuming()
            time.sleep(10)
    except KeyboardInterrupt as k:
        consumer.stop()
        logger.info('stopping the consumer')
    except Exception as e:
        print(e)



if __name__== "__main__":
    logger = logging.getLogger(__name__)
    main(logger)