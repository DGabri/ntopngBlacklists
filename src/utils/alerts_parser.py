from ipaddress import IPv4Address, IPv6Address
from pydantic import BaseModel
from typing import Union
import json
import re


class Alert(BaseModel):
    cli_ip: Union[IPv4Address, IPv6Address, str]
    cli_localhost: bool
    cli_country: str
    cli_asn: int
    
    srv_ip: Union[IPv4Address, IPv6Address, str]
    srv_localhost: bool
    srv_country: str
    srv_asn: int
    srv_port: int = 0
    
    alert_id: int
    info: str
    reason: str
    
class AlertsParser:
    def __init__(self):
        # alert IDs that are relevant for the analysis
        self.relevant_alerts = [40, 41, 42, 61, 68, 79]
        self.no_ip_redaction = [68, 79]
    
    def remove_suffix_ip(self, info_string):
        pattern = (
            r'^'
            r'(?!'
                r'(127\.0\.0\.1|'
                r'localhost|'
                r'10\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
                r'192\.168\.\d{1,3}\.\d{1,3}|'
                r'172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}'
                r')'
            r')'
            r'(\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?)(?=/)'
        )
        return re.sub(pattern, '{REDACTED_IP}', info_string)
    
    def parse_alert(self, json_data):
        
        # validate that json provided is valid
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Invalid JSON string: {e}")
        else:
            data = json_data
        
        # get alerts array from json
        alerts_data = data.get("alerts", [])
        
        parsed_alerts = []
        
        for alert_data in alerts_data:
            try:
                # extract alert id and info string
                alert_id = alert_data.get("alert_id")
                info_string = alert_data.get("info", "")
                
                # skip alerts that are not relevant for the analysis
                if not alert_id in self.relevant_alerts:
                    continue
                
                # clean info string to remove sensitive IP addresses at the beginning
                # This is done to alerts that could contain the host IP inside the info field
                if not alert_id in self.no_ip_redaction:
                    info_string = self.remove_suffix_ip(info_string)
                    
                # try to extract description of malicious fingerprint
                # this is inside alert.json.flow_risk_info.28
                if alert_id == 79:
                    info_string = alert_data.get("json", {}).get("flow_risk_info", {}).get("28", "")
                    
                alert = Alert(
                    cli_ip = alert_data.get("cli_ip", ""),
                    cli_localhost = alert_data.get("cli_localhost", True),
                    cli_country = alert_data.get("cli_country_name", ""),
                    cli_asn = alert_data.get("cli_asn", 0),
                    
                    srv_ip = alert_data.get("srv_ip", ""),
                    srv_localhost = alert_data.get("srv_localhost", True),
                    srv_country = alert_data.get("srv_country_name", ""),
                    srv_asn = alert_data.get("srv_asn", 0),
                    srv_port = alert_data.get("srv_port", 0),
                    
                    alert_id = alert_id,
                    info = info_string
                )
                                
                parsed_alerts.append(alert)
                
            except KeyError as e:
                print(f"Missing field in alert: {e}")
                continue
            except ValidationError as e:
                print(f"Validation error: {e}")
                continue
        
        return parsed_alerts
