#!/usr/bin/env python3
from utils.alerts_generator import AlertsGenerator
from config.config_manager import ConfigManager
from confluent_kafka import Producer
from datetime import datetime
import json
import time
import uuid

class AlertsProducer:
    def __init__(self):
        # config reader and topic getter
        self.config_manager = ConfigManager()
        
        self.config = self.config_manager.get_kafka_producer_config()
        self.topic = self.config_manager.get_producer_topic()
        
        # producer instance initialization from config
        self.producer = Producer(**self.config)
        
        # sample user uuid to send the message in kafka
        self.user_id = uuid.uuid4()

    def _delivery_report(self, err, msg):
        """Delivery report callback called by confluent-kafka producer"""
        if err is not None:
            print(f"Message delivery failed: {err}")

    def send_event(self, timestamp, ip, alert_id, dst_port, info, reason):
        
        event_data = {
            "user_id": str(self.user_id),
            "timestamp": int(timestamp),
            "ip": str(ip),
            "alert_id": int(alert_id),
            "dst_port": int(dst_port),
            "info": str(info),
            "reason": str(reason)
        }
        
        print(f"[PRODUCER] Delivering: {event_data}")
        
        try:
            self.producer.produce(
                topic=self.topic,
                value=json.dumps(event_data).encode('utf-8'),
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
    
    generator = AlertsGenerator()
    producer = AlertsProducer()
    num_alerts = generator.num_alerts
    print("************************************************************")
    print(f"[PRODUCER] Generating: {num_alerts} alerts")
    
    for alert_num in range(0, num_alerts, 1):
        alert = generator.generate_alert()
        generator.print_alert(alert)
        producer.send_event(timestamp=int(time.time()*1000), ip=str(alert.cli_ip), alert_id=int(alert.alert_id), dst_port=int(alert.srv_port), info=str(alert.info), reason=str(alert.reason))
    print("************************************************************")
        
    producer.close()