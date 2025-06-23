msg_schema = """
{
  "type": "record",
  "name": "alertEvent",
  "namespace": "alert.events",
  "fields": [
    {"name": "user_id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "ip", "type": "string"},
    {"name": "alert_id", "type": "int"},
    {"name": "dst_port", "type": "int"},
    {"name": "info", "type": "string"},
    {"name": "reason", "type": "string"}
  ]
}
"""
