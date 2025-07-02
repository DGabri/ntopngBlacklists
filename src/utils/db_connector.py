#!/usr/bin/env python3
from config.config_manager import ConfigManager
from clickhouse_connect import get_client
from uuid import UUID
import re

class ClickhouseConnector:
    def __init__(self):
        self.config = ConfigManager()
        self.db_config = self.config.get_clickhouse_config()
                
        # ch client connector
        self.client = get_client(**self.db_config)
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            if fetch:
                result = self.client.query(query, parameters=params)
                return result.result_rows
            else:
                self.client.command(query, parameters=params)
                return None
        except Exception as e:
            print(f"Query execution error: {e}")
            raise
    
    def query_data(self, query, params=None):
        return self.execute_query(query, params=params, fetch=True)
    
    def insert_data(self, query, params=None):
        return self.execute_query(query, params=params, fetch=False)
    
    def get_ip_events(self, ip):
        """
        Fetch the latest 10 alert events for a specific IP address
        """
        
        query = """
            SELECT timestamp, alert_id, info, reason 
            FROM replicated_blacklist_events 
            WHERE ip = {ip:String}
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        
        params = {'ip': ip}
        return self.query_data(query, params=params)
    
    def get_system_info(self):
        """Get ClickHouse version and hostname."""
        query = "SELECT version(), hostName()"
        return self.query_data(query)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def validate_alert(self, event_dict):
        
        required_fields = ['user_id', 'timestamp', 'ip', 'alert_id', 'dst_port', 'info', 'reason']
        
        # Check for required fields
        missing_fields = [field for field in required_fields if field not in event_dict]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        validated_event = {}
        
        # Validate user_id (UUID)
        try:
            if isinstance(event_dict['user_id'], str):
                validated_event['user_id'] = str(UUID(event_dict['user_id']))
            elif isinstance(event_dict['user_id'], UUID):
                validated_event['user_id'] = str(event_dict['user_id'])
            else:
                raise ValueError("user_id must be a valid UUID string or UUID object")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid user_id: {e}")
        
        # Validate timestamp (UInt64)
        try:
            validated_event['timestamp'] = int(event_dict['timestamp'])
            if validated_event['timestamp'] < 0:
                raise ValueError("timestamp must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("timestamp must be a valid integer")
        
        # Validate IP (String with basic format check)
        ip = str(event_dict['ip']).strip()
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
            raise ValueError("ip must be a valid IPv4 address format")
        validated_event['ip'] = ip
        
        # Validate alert_id (UInt32)
        try:
            validated_event['alert_id'] = int(event_dict['alert_id'])
            if not (0 <= validated_event['alert_id'] <= 4294967295):  # UInt32 range
                raise ValueError("alert_id must be between 0 and 4294967295")
        except (ValueError, TypeError):
            raise ValueError("alert_id must be a valid integer")
        
        # Validate dst_port (UInt16)
        try:
            validated_event['dst_port'] = int(event_dict['dst_port'])
            if not (0 <= validated_event['dst_port'] <= 65535):  # UInt16 range
                raise ValueError("dst_port must be between 0 and 65535")
        except (ValueError, TypeError):
            raise ValueError("dst_port must be a valid port number")
        
        # Validate info and reason (Strings)
        validated_event['info'] = str(event_dict['info']).strip()
        validated_event['reason'] = str(event_dict['reason']).strip()
        
        return validated_event
    
    def insert_alert_blacklist(self, event_dict):
        validated_event = self.validate_alert(event_dict)
        
        query = """
            INSERT INTO replicated_blacklist_events 
            (user_id, timestamp, ip, alert_id, dst_port, info, reason)
            VALUES ({user_id:String}, {timestamp:UInt64}, {ip:String}, 
                    {alert_id:UInt32}, {dst_port:UInt16}, {info:String}, {reason:String})
        """

        self.insert_data(query, params=validated_event)
    
    def insert_alert_blacklist_batch(self, events_list):
        
        if not events_list:
            return
        
        # Validate all events first
        validated_events = [self.validate_alert(event) for event in events_list]
        
        # Prepare data for batch insert
        data_rows = []
        for event in validated_events:
            data_rows.append([
                event['user_id'],
                event['timestamp'], 
                event['ip'],
                event['alert_id'],
                event['dst_port'],
                event['info'],
                event['reason']
            ])
        
        # Use client.insert for efficient batch insert
        self.client.insert(
            'replicated_blacklist_events',
            data_rows,
            column_names=['user_id', 'timestamp', 'ip', 'alert_id', 'dst_port', 'info', 'reason']
        )