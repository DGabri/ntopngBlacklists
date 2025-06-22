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
PARTITION_COUNT=1
RETENTION_MS=1800000
REPLICATION_FACTOR=1

# Topic names
TOPIC_NAME="alerts"


echo "[1] Creating topics "

# create injection attacks topic
kafka-topics --create \
  --bootstrap-server $KAFKA_HOST \
  --topic $TOPIC_NAME \
  --partitions $PARTITION_COUNT \
  --replication-factor $REPLICATION_FACTOR \
  --config retention.ms=$RETENTION_MS \
  --config compression.type=lz4

echo "[1.1] Created topic: $TOPIC_NAME "

# show all topics
echo "[2] List of topics:"
kafka-topics --list --bootstrap-server $KAFKA_HOST

# descibe topic
echo "Topic details:"
kafka-topics --describe --bootstrap-server $KAFKA_HOST --topic $TOPIC_NAME