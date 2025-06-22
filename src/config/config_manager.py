import yaml
import os

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # Use kafka_config.yaml in the same directory as this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'kafka_config.yaml')
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    
        self.kafka_config = config.get("kafka", {})

    def get_producer_config(self):
        producer_config =  {
            "bootstrap.servers": self.kafka_config.get("bootstrap_servers"),
            "client.id": self.kafka_config.get("client_id"),
            "compression.type": self.kafka_config.get("compression_type"),
            "acks": self.kafka_config.get("acks"),
        }
        
        print(f"[CONFIG MANAGER] Producer config: {producer_config}")
        return producer_config

    def get_consumer_config(self):
        consumer_config = {
            "bootstrap.servers": self.kafka_config.get("bootstrap_servers"),
            "group.id": self.kafka_config.get("group_id"),
            "auto.offset.reset": self.kafka_config.get("auto_offset_reset"),
            "enable.auto.commit": self.kafka_config.get("enable_auto_commit"),
            "client.id": self.kafka_config.get("client_id")
        }

        print(f"[CONFIG MANAGER] Consumer config: {consumer_config}")
        return consumer_config
    
    def get_producer_topic(self):
        # get topic name for producer, required string in kafka
        return self.kafka_config.get("producer_topic")
    
    def get_consumer_topic(self):
        # get topic name for consumer, required list in kafka
        return self.kafka_config.get("consumer_topic")
    
#t = ConfigManager()
#t.get_producer_config()
#t.get_consumer_config()