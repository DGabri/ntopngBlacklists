#!/usr/bin/env python3
from ..config.config_manager import ConfigManager
from ..utils.avro_utils import AvroUtils
from ..utils.alerts_generator import AlertsGenerator
from confluent_kafka import Producer
from datetime import datetime
import json
import time

class AlertsProducer:
    def __init__(self):
        # config reader and topic getter
        self.config_manager = ConfigManager()
        self.avro_utils = AvroUtils()
        
        self.config = self.config_manager.get_producer_config()
        self.topic = self.config_manager.get_producer_topic()
        
        # producer instance initialization from config
        self.producer = Producer(**self.config)

    def _delivery_report(self, err, msg):
        """Delivery report callback called by confluent-kafka producer"""
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

    def send_event(self, user_id, timestamp, ip, alert_id, dst_port, info):
        
        event_data = {
            "user_id": int(user_id),
            "timestamp": int(timestamp),
            "ip": str(ip),
            "alert_id": int(alert_id),
            "dst_port": int(dst_port),
            "info": str(info)
        }

        serialized_value = self.avro_utils.serialize_msg(event_data)
        
        try:
            self.producer.produce(
                topic=self.topic,
                value=serialized_value,
                callback=self._delivery_report
            )
            
            self.producer.poll(0)
            
        except Exception as e:
            print(f"Error sending event: {e}")

    def send_batch_events(self, events):
        for event in events:
            self.send_event(**event)
        self.producer.flush()

    def close(self):
        self.producer.flush()

if __name__ == "__main__":
    
    generator = AlertsGenerator(num_alerts=50, alerts_interarrival_ms=0)
    producer = AlertsProducer()
    
    for alert_num in range(0, 200, 1):
        alert = generator.generate_alert()
        producer.send_event(user_id=int(12345), timestamp=int(time.time()*1000), ip=str(alert.cli_ip), alert_id=int(alert.alert_id), dst_port=int(alert.srv_port), info=str(alert.info))
        
    #producer.send_batch_events(sample_events)
    producer.close()