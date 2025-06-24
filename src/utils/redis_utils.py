from config.config_manager import ConfigManager
from datetime import datetime, timedelta
from redis.cluster import RedisCluster
import redis
import json

class RedisClusterConnector:    
    def __init__(self):
        self.config_manager = ConfigManager()

        # if dictionary does not have host or port it will raise an exception
        try:
            self.redis_config = self.config_manager.get_redis_config()
            
            # use 1h of ttl if it is not specified
            self.ttl = self.redis_config.get("ttl", 3600)
            
            # safely access 0, if no bootstrap server is provided the config raises an exception
            bootstrap_servers = self.redis_config.get("bootstrap_servers")[0]
            host = str(bootstrap_servers['host'])
            port = int(bootstrap_servers['port'])
            
            self.connector = RedisCluster(
                host=host, 
                port=port,
                decode_responses=True
            )

        except Exception as e:
            print(f"[REDIS UTILS] Failed to connect to Redis cluster: {e}")
            raise
    
    # generate redis key given an alert id
    def get_alert_id_key(self, alert_id):

        return f"blacklist:{alert_id}:ip_counters"
    
    # increment ip count in alert id blacklist, return new count
    def increment_ip_blacklist(self, alert_id, ip):
        
        key = self.get_alert_id_key(alert_id)
        
        try:
            # pipeline for atomic ops
            pipe = self.connector.pipeline()
            
            # incr ip counter
            pipe.hincrby(key, ip, 1)
            
            # set ttl to key if it is new
            pipe.expire(key, self.ttl)
            
            results = pipe.execute()
            new_count = results[0]
            
            return new_count
            
        except Exception as e:
            print(f"[REDIS UTILS] Error incrementing IP count: {e}")
            raise
    
    # get counts for all the IPs present for a specific alert ID
    def get_ip_counts(self, alert_id):

        key = self.get_alert_id_key(alert_id)
        
        try:
            counts = self.connector.hgetall(key)

            ip_counts = {}
            
            for ip, count in counts.items():
                ip_counts[ip] = int(count)
                
            return ip_counts
        
        except Exception as e:
            print(f"[REDIS UTILS] Error retrieving IPs counts: {e}")
            raise
    
    # get count for a given ip and alert id tuple
    def get_ip_count(self, alert_id, ip):
        
        key = self.get_alert_id_key(alert_id)
        
        try:
            count = self.connector.hget(key, ip)
            
            if count:
                ip_count = int(count)
            else:
                ip_count = 0
                
            return ip_count
        
        except Exception as e:
            print(f"[REDIS UTILS] Error getting IP count: {e}")
            raise
    
    # get all alert ids
    def get_all_alert_ids(self):
        try:
            
            keys = []
            
            for key in self.connector.scan_iter(match="blacklist:*:ip_counters"):
                # get alert id from key
                split_parts = key.split(':')
            
                if len(split_parts) >= 3:
                    # blacklist:{alert_id}:ip_counters
                    alert_id = split_parts[1]
                    
                    keys.append(alert_id)

            return list(set(keys))
        
        except Exception as e:
            print(f"[REDIS UTILS] Error getting alert IDs: {e}")
            raise
        
    def flush_stats(self):
        alert_ids = self.get_all_alert_ids()
        
        for alert_id in alert_ids:
            key = self.get_alert_id_key(alert_id)

            try:
                # create pipeline and delete it
                pipe = self.connector.pipeline()
                pipe.delete(key)
                results = pipe.execute()
                        
            except Exception as e:
                print(f"[REDIS UTILS] Error flushing stats: {e}")
                raise
    
    def print_stats(self):
        try:
            alert_ids = self.get_all_alert_ids()
            
            for alert_id in alert_ids:
                ip_counts = self.get_ip_counts(alert_id)
                
                print("----------- STATS -------------")
                if ip_counts:
                    print(f"IP Counts: {len(ip_counts)}")
                    print(f"Processed messages: {sum(ip_counts.values())}")

                    # sort descending
                    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    for ip, count in sorted_ips:
                        print(f"[ID: {alert_id}] {ip} -> {count}")
                
                print("--------------------------------")
            
        except Exception as e:
            print(f"[REDIS UTILS] Error printing stats: {e}")
