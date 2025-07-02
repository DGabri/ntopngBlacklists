#!/bin/bash

set -e

echo "[*] Waiting for Kafka to be ready at kafka1:29092..."

# Wait until Kafka is reachable
while ! nc -z kafka1 29092; do
  sleep 1
done

echo "[+] Kafka up, creating topis"

# kafka setup
# 30 minutes = 1800000ms for retention
KAFKA_BOOTSTRAP_SERVERS="kafka1:29092,kafka2:29093,kafka3:29094"
PARTITION_COUNT=4
RETENTION_MS=1800000
REPLICATION_FACTOR=3

# Topic name
TOPIC_NAME="blacklist-events"

echo "[1] Creating topics "

if kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --list | grep -wq "^$TOPIC_NAME$"; then
    echo "Topic '$TOPIC_NAME' already exists - skipping creation"
else
  # create topic
  kafka-topics --create \
    --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic $TOPIC_NAME \
    --partitions $PARTITION_COUNT \
    --replication-factor $REPLICATION_FACTOR \
    --config retention.ms=$RETENTION_MS \
    --config compression.type=lz4 \
    --if-not-exists

  echo "[1.1] Created topic: $TOPIC_NAME "
fi

# show all topics
echo "[2] List of topics:"
kafka-topics --list --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS

# descibe topic
echo "Topic details:"
kafka-topics --describe --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --topic $TOPIC_NAME

echo "Kafka setup completed, exiting..."
exit 0;