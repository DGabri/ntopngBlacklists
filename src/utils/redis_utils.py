from redis.cluster import RedisCluster, ClusterNode
from config.config_manager import ConfigManager
from datetime import datetime, timedelta
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
            self.dedup_ttl = self.redis_config.get("dedup_ttl", 3600)
            
            # safely access 0, if no bootstrap server is provided the config raises an exception
            bootstrap_servers = self.redis_config.get("bootstrap_servers")
            
            print(f"[REDIS BOOSTRAP SERVERS] {bootstrap_servers}")
            
            startup_nodes =[]
            for node in bootstrap_servers:
                c = ClusterNode(host=node['host'],port=node['port'])
                startup_nodes.append(c)
                
            
            self.connector = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True
            )

        except Exception as e:
            print(f"[REDIS UTILS] Failed to connect to Redis cluster: {e}")
            raise
    
    ## deduplication handler
    def generate_dedup_key(self, alert):
       
        # get values, else false to handle incorrect received messages
        timestamp = alert.get('timestamp', False)
        alert_id = alert.get('alert_id', False)
        user_id = alert.get('user_id', False)
        ip = alert.get('ip', False)
        info = alert.get('info', False)
        reason = alert.get('reason', False)

        if not (timestamp or alert_id or user_id or ip or info or reason):
            return ""
        
        return f"dedup:{user_id}:{timestamp}:{alert_id}:{ip}:{info}:{reason}"

    def is_duplicate(self, alert):
        try:
            dedup_key = self.generate_dedup_key(alert)
            
            if not len(dedup_key):
                return True
            

            # returns true if kwy was set, so no duplicate. If duplicate returns false
            result = self.connector.set(dedup_key, "processed", nx=True, ex=self.dedup_ttl)
            
            if result:
                return False
            else:
                print(f"[DEDUP] Duplicate alert detected: {dedup_key}")
                return True
                
        except Exception as e:
            print(f"[REDIS UTILS] Error in deduplication check: {e}")
            return False
    
    # generate redis key given an alert id
    def get_alert_id_key(self, alert_id):

        return f"blacklist:{alert_id}:ip_counters"
    
    # increment ip count in alert id blacklist, return new count
    def increment_ip_blacklist(self, alert, alert_id, ip):
        
        key = self.get_alert_id_key(alert_id)
        
        try:
            # check if duplicate, return -1
            if self.is_duplicate(alert):
                return -1
            
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
