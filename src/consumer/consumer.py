#!/usr/bin/env python3
from confluent_kafka import Consumer, KafkaException, KafkaError
from config.config_manager import ConfigManager
from utils.redis_utils import RedisClusterConnector 
import json

class AlertsConsumer:
    def __init__(self):
        # config reader and topic getter
        self.config_manager = ConfigManager()
        
        self.config = self.config_manager.get_kafka_consumer_config()
        self.topic = self.config_manager.get_consumer_topic()
        
        # consumer instance initialization from config
        self.consumer = Consumer(**self.config)
        self.consumer.subscribe(self.topic)
        
        # redis connector
        self.redis = RedisClusterConnector()
        
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
                event = msg.value().decode('utf-8')
                print(f"[CONSUMER] Message received: {event}")
                self.process_msg(event)

        except KeyboardInterrupt:
            print("Consumer interrupted by user")

        finally:
            print("Closing consumer...")
            self.consumer.close()

    def is_valid_ip(self, ip):
        # check some ips, it is impossible to receive query and alerts from these IPs
        # prevent attacker injection, sample IPs used from google DNS and cloudflare
        invalid_ips = ['8.8.8.8', '1.1.1.1']
        
        return ip not in invalid_ips
    
    # clean message and update redis queue
    def process_msg(self, msg):
        
        try:
            msg = json.loads(msg)
            alert_id = int(msg.get("alert_id", -1))
            ip = str(msg.get("ip", ""))
            print(f"[CONSUMER] Received: {msg}")
            
            if (alert_id > 0) and self.is_valid_ip(ip):
                count = self.redis.increment_ip_blacklist(alert_id, ip)
                
                print(f"[CONSUMER] IP: {ip} -> {count}")
            else:
                print(f"[INVALID IP] {ip}")
        except Exception as e:
            print(f"***********\n[ERROR PROCESSING MESSAGE] {msg}\n {e}\n***********\n")
            
    
if __name__ == '__main__':
    consumer = AlertsConsumer()
    consumer.consume_loop()
