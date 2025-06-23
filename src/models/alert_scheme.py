from ipaddress import IPv4Address, IPv6Address
from pydantic import BaseModel
from typing import Union

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
    