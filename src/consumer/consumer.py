#!/usr/bin/env python3
from confluent_kafka import Consumer, KafkaException, KafkaError
from ..config.config_manager import ConfigManager
from ..utils.avro_utils import AvroUtils

class AlertsConsumer:
    def __init__(self):
        # config reader and topic getter
        self.config_manager = ConfigManager()
        self.avro_utils = AvroUtils()
        
        self.config = self.config_manager.get_consumer_config()
        self.topic = self.config_manager.get_consumer_topic()
        
        # consumer instance initialization from config
        self.consumer = Consumer(**self.config)
        self.consumer.subscribe(self.topic)
        

    def consume_loop(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue  # No message received
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        continue
                    else:
                        raise KafkaException(msg.error())

                # Deserialize Avro message
                event = self.avro_utils.deserialize_msg(msg.value())

                # Print received event and topic info
                print(f"Received event from topic {msg.topic()} partition {msg.partition()} offset {msg.offset()}:")
                print(event)

        except KeyboardInterrupt:
            print("Consumer interrupted by user")

        finally:
            print("Closing consumer...")
            self.consumer.close()


if __name__ == '__main__':
    consumer = AlertsConsumer()
    consumer.consume_loop()
