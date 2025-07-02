-- this is the local replicated table
-- this is where data stays and then replicated to other replicas in the same shard as defined in ./clickhouseX/config/macros.xml
CREATE TABLE IF NOT EXISTS blacklist_events ON CLUSTER 'cluster_1S_2R' (
    user_id UUID,
    timestamp UInt64,
    ip String,
    alert_id UInt32,
    dst_port UInt16,
    info String,
    reason String
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/blacklist_events', '{replica}'
)
ORDER BY (timestamp, alert_id);

-- distributed table, like a view to the table above, stores metadata on whic remote table needs too query and distribute writes
CREATE TABLE IF NOT EXISTS replicated_blacklist_events ON CLUSTER 'cluster_1S_2R'
AS default.blacklist_events
ENGINE = Distributed('cluster_1S_2R', default, blacklist_events, rand());

