# Architecture Overview

## System Architecture

This real-time manufacturing analytics platform is built on AWS and follows data engineering best practices from the AWS Data Engineer Associate (DEA-C01) certification.

### Architecture Diagram

```
┌─────────────────┐
│  Manufacturing  │
│    Sensors      │
│   (Simulated)   │
└────────┬────────┘
         │
         │ Stream Data
         ▼
┌─────────────────────────────┐
│  Amazon Kinesis Data Stream │ ◄─── Encrypted with KMS
│   (2 shards, 24h retention) │
└────────┬────────────────────┘
         │
         │ Real-time Processing
         ▼
┌─────────────────────────────────┐
│ Amazon Managed Service for      │
│      Apache Flink               │
│  - Windowed Aggregation         │
│  - Anomaly Detection            │
│  - Fault Tolerance (Checkpoint) │
└────────┬────────────────────────┘
         │
         │ Write Metrics
         ▼
┌─────────────────────────────┐
│   Amazon Timestream         │
│   - Time-series Database    │ ◄─── Encrypted with KMS
│   - Fast Query Performance  │
└────────┬────────────────────┘
         │
         │ Query Data
         ▼
┌─────────────────────────────┐
│        Grafana              │
│   Live Dashboards           │
└─────────────────────────────┘

         Monitoring & Alerting
┌─────────────────────────────┐
│   Amazon CloudWatch         │
│   - Metrics & Logs          │
│   - Dashboards              │
│   - Alarms → SNS            │
└─────────────────────────────┘
```

## Components

### 1. Data Ingestion Layer
- **Amazon Kinesis Data Streams**: Ingests sensor data with low latency
  - Provisioned mode with configurable shards
  - KMS encryption at rest
  - Shard-level metrics enabled
  - 24-hour retention period

### 2. Processing Layer
- **Amazon Managed Service for Apache Flink**: Processes and transforms data
  - Real-time windowed aggregations (1-minute tumbling windows)
  - Computes: avg, min, max values per machine/sensor
  - Tracks anomaly counts
  - Checkpointing enabled for fault tolerance
  - Auto-scaling based on throughput

### 3. Storage Layer
- **Amazon Timestream**: Purpose-built time-series database
  - Memory store: 24 hours (fast queries)
  - Magnetic store: 90 days (cost-effective)
  - Automatic data tiering
  - KMS encryption
  - Rejected data stored in S3

### 4. Visualization Layer
- **Grafana**: Real-time operational dashboards
  - Timestream data source integration
  - Multiple visualization types (time-series, stats, tables)
  - 5-second auto-refresh
  - Pre-built dashboards for common metrics

### 5. Monitoring & Alerting
- **Amazon CloudWatch**: Comprehensive monitoring
  - Kinesis stream metrics (iterator age, throughput)
  - Flink application metrics (uptime, checkpoints, CPU)
  - Custom dashboards
  - SNS alarms for critical events

## Data Flow

1. **Data Generation**: Sensor data generator simulates manufacturing equipment
   - 5 machines × 5 sensor types
   - Temperature, pressure, vibration, power consumption, cycle time
   - Random anomaly injection (5% probability)

2. **Data Ingestion**: Records sent to Kinesis Data Streams
   - Batch writes for efficiency
   - Partition key: machine_id (ensures ordering per machine)
   - JSON format with metadata

3. **Stream Processing**: Flink application processes events
   - Reads from Kinesis with watermarks for late data
   - Groups by machine_id and sensor_type
   - 1-minute tumbling windows
   - Computes aggregations (avg, min, max, count, anomalies)

4. **Data Storage**: Aggregated metrics written to Timestream
   - Multi-measure records
   - Dimensions: machine_id, sensor_type, location, production_line
   - Measures: avg_value, min_value, max_value, record_count, anomaly_count

5. **Visualization**: Grafana queries Timestream
   - Real-time charts and graphs
   - Statistical aggregations
   - Alert thresholds visualization

## Security Architecture

### Encryption
- **At Rest**: All data encrypted with AWS KMS
  - Separate KMS keys for Kinesis, Timestream, S3, SNS
  - Automatic key rotation enabled
  - 10-day deletion window

- **In Transit**: TLS encryption for all service communications

### IAM Least Privilege
- **Flink Execution Role**: Limited to:
  - Read from specific Kinesis stream
  - Write to specific Timestream table
  - Access to specific S3 bucket for artifacts
  - CloudWatch Logs for application logs
  - KMS decrypt permissions for required keys

- **Data Generator Role**: Limited to:
  - Write to specific Kinesis stream
  - KMS permissions for Kinesis encryption

- **Grafana Role**: Limited to:
  - Read from Timestream database/table
  - KMS decrypt for Timestream

### Network Security
- S3 buckets: Public access blocked
- Timestream: IAM-based access control
- CloudWatch: Encrypted logs

## Fault Tolerance & Reliability

### Checkpointing
- Flink checkpoints every 60 seconds
- State stored in managed Flink state backend
- Automatic recovery on failure

### Auto-scaling
- Flink parallelism matches shard count
- Auto-scaling enabled for dynamic workloads

### Monitoring
- CloudWatch alarms for:
  - High iterator age (processing lag)
  - No incoming records (data pipeline failure)
  - Flink application downtime
  - Checkpoint failures

### Data Durability
- Kinesis: 24-hour retention for replay
- Timestream: Automatic replication across AZs
- S3 versioning enabled for artifacts

## Performance Optimization

### Kinesis
- Multiple shards for parallel processing
- Batch writes to reduce API calls
- Enhanced monitoring enabled

### Flink
- Parallelism configured per shard count
- Windowing for efficient aggregation
- Asynchronous Timestream writes

### Timestream
- Memory store for recent data (fast queries)
- Magnetic store for historical data (cost-effective)
- Query optimization with proper dimensions

## Cost Optimization

1. **Right-sizing**: Provisioned capacity based on expected load
2. **Data Lifecycle**: Automatic tiering to magnetic store after 24h
3. **Monitoring**: CloudWatch metrics retention policies
4. **S3 Lifecycle**: Rejected data cleanup after 30 days

## Scalability Considerations

- **Horizontal Scaling**: Add Kinesis shards for higher throughput
- **Flink Parallelism**: Automatically adjusts with shard count
- **Timestream**: Serverless, automatically scales
- **Grafana**: Can be deployed in HA configuration

## DEA-C01 Best Practices Applied

1. ✓ **Data Ingestion**: Kinesis for streaming data ingestion
2. ✓ **Data Processing**: Managed Flink for real-time processing
3. ✓ **Data Storage**: Purpose-built database (Timestream) for time-series
4. ✓ **Security**: Encryption at rest and in transit, IAM least privilege
5. ✓ **Monitoring**: CloudWatch metrics, logs, and alarms
6. ✓ **Fault Tolerance**: Checkpointing, auto-recovery, data retention
7. ✓ **Cost Optimization**: Data lifecycle policies, right-sizing
8. ✓ **Infrastructure as Code**: Terraform for reproducible deployments
