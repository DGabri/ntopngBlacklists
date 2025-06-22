msg_schema = """
{
  "type": "record",
  "name": "SecurityEvent",
  "namespace": "security.events",
  "fields": [
    {"name": "user_id", "type": "long"},
    {"name": "timestamp", "type": "long"},
    {"name": "ip", "type": "string"},
    {"name": "alert_id", "type": "int"},
    {"name": "dst_port", "type": "int"},
    {"name": "info", "type": "string"},
    {"name": "reason", "type": "string"}
  ]
}
"""