import yaml
import os

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # get config.yaml
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config.yaml')
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_redis_config(self):
        self.redis_config = self.config.get("redis", {})

        bootstrap_servers = []

        for server in self.redis_config.get("bootstrap_servers", []):
            try:
                host, port = server.split(':')
                bootstrap_servers.append({"host": host, "port": int(port)})
            except ValueError:
                print(f"Invalid format reading redis config. Please use - 'host:port' ")
                continue 
        
        # get ttl
        ttl = self.redis_config.get("ttl")

        if len(bootstrap_servers):
            # return redis configuration if at least one bootstrap server is provided, else raise exception
            redis_config = {
                "bootstrap_servers": bootstrap_servers,
                "ttl": ttl,
                "dedup_ttl": self.redis_config.get("dedup_ttl", 3600)
            }
            print(f"[CONFIG MANAGER] Redis config: {redis_config}")
            return redis_config
        
        # no bootstrap server found        
        raise Exception("No boostrap server found, please set it in config.yaml")
        
    def get_kafka_producer_config(self):
        self.kafka_config = self.config.get("kafka", {})
        
        producer_config =  {
            "bootstrap.servers": self.kafka_config.get("bootstrap_servers", "localhost:9092"),
            "client.id": self.kafka_config.get("client_id", "blacklist-generator"),
            "compression.type": self.kafka_config.get("compression_type", "lz4"),
            "acks": self.kafka_config.get("acks", "all"),
            "enable.idempotence": self.kafka_config.get("enable_idempotence", True),
        }
        
        print(f"[CONFIG MANAGER] Kafka Producer config: {producer_config}")
        return producer_config

    def get_kafka_consumer_config(self):
        self.kafka_config = self.config.get("kafka", {})
        consumer_config = {
            "bootstrap.servers": self.kafka_config.get("bootstrap_servers", "localhost:9092"),
            "group.id": self.kafka_config.get("group_id", "alerts-group"),
            "auto.offset.reset": self.kafka_config.get("auto_offset_reset", "earliest"),
            "enable.auto.commit": self.kafka_config.get("enable_auto_commit", True),
            "client.id": self.kafka_config.get("client_id", "blacklist-generator")
        }

        print(f"[CONFIG MANAGER] Consumer config: {consumer_config}")
        return consumer_config
    
    def get_producer_topic(self):
        # get topic name for producer, required string in kafka
        return self.kafka_config.get("producer_topic")
    
    def get_consumer_topic(self):
        # get topic name for consumer, required list in kafka
        return self.kafka_config.get("consumer_topic")
    
    def get_alerts_generator_config(self):
        self.alert_generator_config = self.config.get("alerts_generator", {})
        
        alert_generator_config = {
            "num_alerts": self.alert_generator_config.get("num_alerts", 10000),
            "num_ip_addresses": self.alert_generator_config.get("num_ip_addresses", 100),
            "alert_interarrival_ms": self.alert_generator_config.get("alert_interarrival_ms", 10)
        }

        print(f"[CONFIG MANAGER] Alert generator config: {alert_generator_config}")
        return alert_generator_config