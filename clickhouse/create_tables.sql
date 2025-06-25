CREATE TABLE IF NOT EXISTS blacklist_events (
    user_id UUID,
    timestamp UInt64,
    ip String,
    alert_id UInt32,
    dst_port UInt16,
    info String,
    reason String
) ENGINE = MergeTree()
ORDER BY (timestamp, alert_id);