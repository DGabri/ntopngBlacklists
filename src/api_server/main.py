from utils.redis_utils import RedisClusterConnector
from .db_connector import ClickhouseConnector
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any
import json

app = FastAPI(title="Blacklists API", version="1.0.0")
redis_connector = RedisClusterConnector()
db = ClickhouseConnector(host="clickhouse1", port=9010, user='default', password='')
alert_ids = [40, 41, 42, 61, 68, 79]

categories_mapping = {
    40: "Injection Attack",
    41: "Injection Attack",
    68: "Injection Attack",
    42: "Scanner",
    79: "Scanner",
    61: "SSH Bruteforce"
}

@app.get("/blacklists/{category}")
async def get_blacklist(alert_id: int, format: Optional[str] = Query(default="json", regex="^(txt|json)$")):

    print(f"Requested alert_id: {alert_id}")
    
    # check if alert id is valid
    if alert_id not in alert_ids:
        raise HTTPException(status_code=404, detail=f"Alert_id '{alert_id}' not found")
    
    data = redis_connector.get_ip_counts(alert_id)
    print(data)
    
    if format == "txt":
        # Format as tab-separated text: key \t value
        txt_content = "\n".join([f"{key}\t{value}" for key, value in data.items()])
        return PlainTextResponse(
            content=txt_content,
            headers={"Content-Disposition": f"attachment; filename={category}_blacklist.txt"}
        )
    else:
        return {
            "category": categories_mapping.get(alert_id, ""),
            "blacklist": data
        }

@app.get("/ip_events")
async def get_events(ip: str):
    print(f"Requested IP: {ip}")
    print(f"Limit: {limit}")
    
    events = db.get_ip_events(ip)
    print(events)
    return {
        "ip": ip,
        "events": events
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)