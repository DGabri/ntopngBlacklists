import time

class AlertsGenerator:
    
    def __init__(self, num_alerts, alerts_interarrival_ms):
        self.num_alerts = num_alerts
        self.alerts_interval = alerts_interarrival_ms
        
    def generate_ip(self, is_localhost):
        pass
    
    def generate_alert_id(self):
        pass
    
    def generate_alert_description(self, alert_id):
        pass
    
    def generate_country_code(self):
        pass
    
    def generate_asn(self):
        pass
    
    def generate_alerts(self):
        
        for alert_idx in range(0, self.num_alerts):
            alert_id = self.generate_alert_id()
            
            cli_ip = self.generate_ip()
            
            srv_ip = self.generate_ip()
            
            # / 1000 to get ms
            time.sleep(self.alerts_interval / 1000)