"""Single consumer that reads from topics."""

from confluent_kafka import Consumer, KafkaError, TopicPartition
import json
import time

def main():

    def revoke_function(consumer, partitions):
        print('revoke function is called.')

    def assign_function(consumer, partitions):
        """ executes before consumer starts reading message from kafka. """
        # This function will be called whenever partitions are assigned to our consumer
        print(f"Partitions assigned: {partitions}")
        
        # For each assigned partition, set its offset to the beginning
        for partition in partitions:
            # Convert to TopicPartition object if it isn't already
            if not isinstance(partition, TopicPartition):
                partition = TopicPartition(partition.topic, partition.partition)
            
            # Set the offset to OFFSET_BEGINNING (-2)
            partition.offset = -2  # -2 is the special value for OFFSET_BEGINNING
        
        # Assign these modified partitions (with reset offsets) back to the consumer
        consumer.assign(partitions)
        print("All partition offsets have been reset to beginning")

    def lost_function(consumer, partitions):
        """ executes at last before consumer is closed. """
        print('lost function is called.')


    consumer_configuration = {
        'bootstrap.servers': 'kafka:9092',
        'group.id': "user-events-processor",
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 5000,           # Commit every 5 seconds
        'max.poll.interval.ms': 300000,            # Max time between polls (5 min)
        'session.timeout.ms': 30000,               # Session timeout (30 sec)
    }

    USER_EVENT_TOPIC = "user-events"

    consumer = Consumer(consumer_configuration)

    try:
        consumer.subscribe([USER_EVENT_TOPIC]
            , on_assign=assign_function
            , on_lost=lost_function
            , on_revoke=revoke_function
        )
        print(f'Subscribed to topic: {USER_EVENT_TOPIC}')

        while True:
            msg = consumer.poll(timeout=2)

            if msg is None:
                print('no message read')
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition - not really an error, just no more messages
                    print(f"Reached end of partition {msg.topic()}/{msg.partition()}")
                else:
                    # Actual error occurred
                    print(f"Error while consuming: {msg.error()}")
            else:
                message_value =  msg.value() 
                event = json.loads(message_value.decode('utf-8'))
                print(f"Processing user event: {event}")
            time.sleep(1)


    except KeyboardInterrupt:
        print('stopping consumer')
    finally:
        consumer.close()
        print("Consumer closed.")


if __name__ == "__main__":
    main()