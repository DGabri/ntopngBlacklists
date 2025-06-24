#!/bin/bash

# Container names
CONTAINERS=("clickhouse1" "clickhouse2")
INIT_SQL_FILE=${1:-./clickhouse/create_tables.sql}


# Init each container
for CONTAINER in "${CONTAINERS[@]}"; do
  echo "Waiting $CONTAINER to be available"

  until docker exec -it "$CONTAINER" clickhouse-client -q "SELECT 1" &>/dev/null; do
    echo "Waiting $CONTAINER"
    sleep 2
  done

  echo "$CONTAINER ready"

  docker exec -i "$CONTAINER" clickhouse-client --multiquery < "$INIT_SQL_FILE"
  echo "Script executed $CONTAINER complete."
done
