from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic.networks import IPvAnyAddress
import json


class alert(BaseModel):
    cli_ip: IPvAnyAddress
    cli_localhost: bool
    cli_country: str
    cli_asn: int
    
    srv_ip: IPvAnyAddress
    srv_localhost: bool
    srv_country: str
    srv_asn: int
    
    alert_id: int
    info: dict
    
    
alerts_list = []

with open('./alerts/alerts_aitest_interhost.jsonl', 'r') as json_file:
    alerts_list = list(json_file)

for json_str in alerts_list:
    result = json.loads(json_str)
    print(f"result: {result}")

for alerts in alerts_list:
    alert = json.loads(alerts_list[0]).get("alerts", [])