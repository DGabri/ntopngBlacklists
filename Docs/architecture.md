- No key needed as i do not need to always have the same ip:alert in a partition, i just need to process the message, order is not needed
- sudo chown 1000:1000 /tmp/kafka-data
- sudo chown -R 1000:1000 /tmp/zookeeper-data /tmp/zookeeper-logs

This project consists in creating a system to generate distributed network blacklists and threat intelligence platform based on alerts received from distributed network probes.
The alerts received enable us to create a solutions similar to abuseIP but with more details.
We are able to detect specific ssh versions used by bruteforce scanner, SQL RCE XSS injection content, mail auth attempt and similar events.

The architecture is composed of:
- Producers: which are python scripts that collect alerts on the network probe and forward on specific kafka topics to a broker recorded alerts
- Consumers: read from kafka partitions, store in memory a map IP -> alerts, alerts count, info query and periodically dump to a replicated db instance
- REST Server: given an ip provides information on the threat intelligence of that IP