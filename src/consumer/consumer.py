#!/usr/bin/env python3
from confluent_kafka import Consumer, KafkaException, KafkaError
from config.config_manager import ConfigManager
from utils.redis_utils import RedisClusterConnector 
from utils.db_connector import ClickhouseConnector 
import json

class AlertsConsumer:
    def __init__(self):
        # config reader and topic getter
        print("[CONSUMER] Setting up config manager")
        self.config_manager = ConfigManager()
        
        print("[CONSUMER] Getting configuration")
        self.config = self.config_manager.get_kafka_consumer_config()
        self.topic = self.config_manager.get_consumer_topic()
        print(f"[CONSUMER] Got configuration: {self.config} topic: {self.topic}")
        
        # consumer instance initialization from config
        self.consumer = Consumer(**self.config)
        print("[CONSUMER] Initialized consumer connector")
        
        self.consumer.subscribe(self.topic)
        self.consumed_messages = 0
        print("[CONSUMER] Setting up Redis connector")
        
        # redis connector
        self.redis = RedisClusterConnector()
        print("[CONSUMER] INITIALIZED")
        self.db = ClickhouseConnector()

        
    def consume_loop(self):
        print("[CONSUMER] Starting consume loop...")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    #print(f"[CONSUMER] NO NEW MESSAGE")
                    continue
                if msg.error():
                    # end of partition
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                
                self.process_msg(msg.value().decode('utf-8'))
                
        except Exception as e:
            print(f"[CONSUMER EXCEPTION] Error: {e}")
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
            alert = json.loads(msg)
            alert_id = int(alert.get("alert_id", -1))
            ip = str(alert.get("ip", ""))
            print(f"[CONSUMER] Received: {alert}")
            
            if (alert_id > 0) and self.is_valid_ip(ip):
                count = self.redis.increment_ip_blacklist(alert, alert_id, ip)
                
                # if -1 it is duplicate
                if count < 0:
                    print(f"[CONSUMER] Deduplicated message for {ip}. Total messages seen: {self.consumed_messages}")
                else:
                    self.consumed_messages += 1
                    print(f"[CONSUMER] Processed message for {ip}. New count: {count}. Total processed: {self.consumed_messages}")
                    self.db.insert_alert_blacklist(alert)
                
                print(f"[CONSUMER] IP: {ip} -> {count}")
            else:
                print(f"[INVALID IP] {ip}")
        except Exception as e:
            print(f"***********\n[ERROR PROCESSING MESSAGE] {msg}\n {e}\n***********\n")
            
    
if __name__ == '__main__':
    consumer = AlertsConsumer()
    consumer.consume_loop()
