CREATE TABLE kafka_messages1 (
    user_id UUID,
    timestamp UInt64,
    ip String,
    alert_id UInt32,
    dst_port UInt16,
    info String,
    reason String
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'blacklist-events',
    kafka_group_name = 'clickhouse_alerts_group1',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n',
    kafka_num_consumers = 1;

CREATE TABLE clean_alerts (
    user_id UUID,
    timestamp UInt64,
    ip String,
    alert_id UInt32,
    dst_port UInt16,
    info String,
    reason String
)
ENGINE = ReplacingMergeTree()
ORDER BY (user_id, alert_id, timestamp); 

CREATE MATERIALIZED VIEW mv_alerts_consumer TO clean_alerts AS
SELECT
    user_id,
    timestamp,
    ip,
    alert_id,
    dst_port,
    info,
    reason
FROM kafka_messages1;