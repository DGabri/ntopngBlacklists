#!/bin/bash

set -e

echo "[*] Waiting for Kafka to be ready at kafka:29092..."

# Wait until Kafka is reachable
while ! nc -z kafka 29092; do
  sleep 1
done

echo "[+] Kafka up, creating topis"

# kafka setup
# 30 minutes = 1800000ms for retention
KAFKA_HOST="kafka:29092"
PARTITION_COUNT=10
RETENTION_MS=1800000
REPLICATION_FACTOR=1

# Topic names
TOPIC_NAME="blacklist-events"

if kafka-topics --bootstrap-server kafka:29092 --list | grep -wq "$TOPIC_NAME"; then
  # create topic
  kafka-topics --create \
    --bootstrap-server $KAFKA_HOST \
    --topic $TOPIC_NAME \
    --partitions $PARTITION_COUNT \
    --replication-factor $REPLICATION_FACTOR \
    --config retention.ms=$RETENTION_MS \
    --config compression.type=lz4 \
    --if-not-exists

  echo "[1.1] Created topic: $TOPIC_NAME "
else
    echo "Topic 'blacklist-events' already exists - skipping creation"
fi

echo "[1] Creating topics "



# show all topics
echo "[2] List of topics:"
kafka-topics --list --bootstrap-server $KAFKA_HOST

# descibe topic
echo "Topic details:"
kafka-topics --describe --bootstrap-server $KAFKA_HOST --topic $TOPIC_NAME