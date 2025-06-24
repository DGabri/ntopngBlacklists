#!/usr/bin/env python3
from utils.redis_utils import RedisClusterConnector
import time

redis = RedisClusterConnector()
alert_ids = [40, 41, 42, 61, 68, 79]

while True:
    print("**************************************************8")
    for alert_id in alert_ids:
        redis.print_stats()
    time.sleep(5)