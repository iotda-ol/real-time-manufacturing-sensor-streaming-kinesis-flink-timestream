# Quick Start Guide

Get the manufacturing analytics platform running in under 30 minutes.

## Prerequisites

- AWS Account with admin access
- AWS CLI configured (`aws configure`)
- Maven 3.6+, Java 11+, Python 3.8+, Terraform 1.0+

## 5-Minute Setup

### 1. Clone and Configure

```bash
git clone https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream.git
cd real-time-manufacturing-sensor-streaming-kinesis-flink-timestream

# Create config
cat > terraform/terraform.tfvars <<EOF
aws_region          = "us-east-1"
environment         = "dev"
project_name        = "manufacturing-analytics"
kinesis_shard_count = 2
alarm_email         = "your-email@example.com"
EOF
```

### 2. Build Application

```bash
make build
```

### 3. Deploy Infrastructure

```bash
make deploy
```

This creates:
- Kinesis Data Stream
- Flink Application
- Timestream Database
- CloudWatch Monitoring
- IAM Roles & Policies
- KMS Keys
- S3 Buckets

**Time**: ~10 minutes

### 4. Upload Flink JAR

```bash
make upload
```

### 5. Start Flink Application

```bash
make start-flink
```

Wait 2-3 minutes for Flink to start (status: RUNNING)

### 6. Generate Data

```bash
make start-generator
```

You should see:
```
✓ Batch sent: 10 succeeded, 0 failed
✓ Sent: M001 | temperature | 72.5 celsius | NORMAL
✓ Sent: M002 | pressure | 105.3 psi | NORMAL
```

### 7. Verify Data

In another terminal:

```bash
# View logs
make logs

# Query Timestream
make query
```

## What You've Built

### Architecture

```
Sensors → Kinesis → Flink → Timestream → Grafana
                      ↓
                 CloudWatch
```

### Components

1. **Kinesis Stream**: Ingests 1000s of records/second
2. **Flink App**: Processes in real-time with 1-min windows
3. **Timestream**: Stores time-series metrics
4. **CloudWatch**: Monitors everything
5. **Grafana**: Visualizes metrics (setup required)

### Data Flow

1. Generator creates sensor readings (5 machines × 5 sensors)
2. Kinesis receives batches of records
3. Flink aggregates over 1-minute windows
4. Timestream stores: avg, min, max, count, anomalies
5. Query anytime with < 1s latency

## Quick Commands

```bash
# Build
make build              # Compile Flink app

# Deploy
make deploy             # Create infrastructure
make upload             # Upload JAR to S3
make start-flink        # Start processing

# Run
make start-generator    # Generate sensor data

# Monitor
make logs              # View Flink logs
make query             # Query Timestream

# Clean
make clean             # Remove build artifacts
make destroy           # Delete all infrastructure
```

## Access URLs

After deployment, access:

1. **AWS Console**
   - Kinesis: https://console.aws.amazon.com/kinesis
   - Flink: https://console.aws.amazon.com/kinesisanalytics
   - Timestream: https://console.aws.amazon.com/timestream
   - CloudWatch: https://console.aws.amazon.com/cloudwatch

2. **CloudWatch Dashboard**
   ```bash
   DASHBOARD_NAME=$(cd terraform && terraform output -raw cloudwatch_dashboard_name)
   echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${DASHBOARD_NAME}"
   ```

## Sample Queries

### Query Average Temperature

```bash
aws timestream-query query --query-string "
SELECT machine_id, 
       AVG(measure_value::double) as avg_temp 
FROM manufacturing-analytics-db-dev.sensor_metrics 
WHERE measure_name = 'avg_value' 
  AND sensor_type = 'temperature' 
  AND time > ago(1h) 
GROUP BY machine_id
"
```

### Find Anomalies

```bash
aws timestream-query query --query-string "
SELECT machine_id, 
       sensor_type, 
       SUM(measure_value::bigint) as total_anomalies 
FROM manufacturing-analytics-db-dev.sensor_metrics 
WHERE measure_name = 'anomaly_count' 
  AND time > ago(1h) 
GROUP BY machine_id, sensor_type 
ORDER BY total_anomalies DESC
"
```

### Count Total Records

```bash
aws timestream-query query --query-string "
SELECT COUNT(*) as total_records 
FROM manufacturing-analytics-db-dev.sensor_metrics 
WHERE time > ago(1h)
"
```

## Grafana Setup

### Option 1: Amazon Managed Grafana

1. Create workspace in AWS Console
2. Add Timestream data source
3. Import dashboard from `grafana/dashboard.json`

### Option 2: Self-Hosted

```bash
# Install Grafana
docker run -d -p 3000:3000 grafana/grafana

# Add Timestream plugin
docker exec <container> grafana-cli plugins install grafana-timestream-datasource

# Access: http://localhost:3000 (admin/admin)
# Add data source using grafana/datasource.yaml
# Import dashboard from grafana/dashboard.json
```

## Monitoring

### Key Metrics

**Kinesis**
- IncomingRecords: Records/second
- IteratorAge: Processing lag (ms)

**Flink**
- uptime: Application health
- numRecordsInPerSecond: Processing rate
- cpuUtilization: Resource usage

**Timestream**
- Record count: Total records stored
- Query performance: Response time

### Alarms

Configured for:
- High iterator age (>1 minute)
- No incoming records
- Flink downtime
- Checkpoint failures

Check email for alarm notifications.

## Troubleshooting

### Issue: Data Generator Fails

```bash
# Check stream exists
aws kinesis list-streams

# Verify permissions
aws iam get-role-policy --role-name manufacturing-analytics-data-generator-role-dev --policy-name kinesis-write-policy

# Test write
aws kinesis put-record --stream-name manufacturing-analytics-sensor-stream-dev --partition-key test --data dGVzdA==
```

### Issue: Flink Not Starting

```bash
# Check status
aws kinesisanalyticsv2 describe-application --application-name manufacturing-analytics-sensor-processor-dev

# View errors
aws logs tail /aws/kinesis-analytics/manufacturing-analytics-sensor-processor-dev

# Verify JAR exists
aws s3 ls s3://$(cd terraform && terraform output -raw s3_bucket_name)/flink-app.jar
```

### Issue: No Data in Timestream

```bash
# Check table
aws timestream-write describe-table --database-name manufacturing-analytics-db-dev --table-name sensor_metrics

# Check Flink logs for errors
aws logs filter-log-events --log-group-name /aws/kinesis-analytics/manufacturing-analytics-sensor-processor-dev --filter-pattern ERROR

# Verify IAM permissions
aws iam get-role-policy --role-name manufacturing-analytics-flink-role-dev --policy-name timestream-write-policy
```

## Cost Management

### Estimated Costs (us-east-1)

- **Running 24/7**: ~$341/month
- **Business Hours Only** (8h/day, 5d/week): ~$85/month

### Cost Reduction Tips

1. **Stop Flink when not needed**
   ```bash
   aws kinesisanalyticsv2 stop-application --application-name manufacturing-analytics-sensor-processor-dev
   ```

2. **Reduce shard count** (lower throughput)
   ```hcl
   kinesis_shard_count = 1
   ```

3. **Shorter retention periods**
   ```hcl
   timestream_memory_retention_hours = 12
   timestream_magnetic_retention_days = 30
   ```

## Next Steps

1. **Customize**: Modify sensor types, add machines
2. **Extend**: Add ML-based anomaly detection
3. **Integrate**: Connect to existing systems
4. **Optimize**: Tune for your workload
5. **Scale**: Add shards, increase parallelism
6. **Secure**: Review IAM policies, enable MFA

## Resources

- [Full Documentation](DEPLOYMENT.md)
- [Architecture Details](ARCHITECTURE.md)
- [Testing Guide](TESTING.md)
- [Terraform Docs](../terraform/)
- [AWS Documentation](https://docs.aws.amazon.com/)

## Support

- GitHub Issues: Report bugs
- AWS Support: Infrastructure questions
- Documentation: Check docs/ folder

## Cleanup

When done testing:

```bash
# Stop everything
Ctrl+C  # Stop data generator
make destroy  # Delete all infrastructure
```

**Warning**: This deletes all data permanently!

## Success Checklist

- [ ] Infrastructure deployed (Terraform apply succeeded)
- [ ] Flink application running (status: RUNNING)
- [ ] Data generator sending records
- [ ] Kinesis receiving data (check CloudWatch)
- [ ] Flink processing data (check logs)
- [ ] Timestream has records (query returns data)
- [ ] CloudWatch dashboard shows metrics
- [ ] Grafana connected (optional)
- [ ] Alarms configured and tested

✅ If all checked, you have a working real-time analytics platform!

## What's Running

```bash
# Check all components
echo "=== Infrastructure Status ==="
cd terraform && terraform show | grep "# aws_" | wc -l && echo "resources created"

echo "=== Kinesis Stream ==="
aws kinesis describe-stream --stream-name manufacturing-analytics-sensor-stream-dev --query 'StreamDescription.StreamStatus'

echo "=== Flink Application ==="
aws kinesisanalyticsv2 describe-application --application-name manufacturing-analytics-sensor-processor-dev --query 'ApplicationDetail.ApplicationStatus'

echo "=== Timestream Table ==="
aws timestream-write describe-table --database-name manufacturing-analytics-db-dev --table-name sensor_metrics --query 'Table.TableStatus'

echo "=== Recent Records ==="
aws timestream-query query --query-string "SELECT COUNT(*) FROM manufacturing-analytics-db-dev.sensor_metrics WHERE time > ago(5m)"
```

## Learning Resources

- [AWS Kinesis Best Practices](https://docs.aws.amazon.com/streams/latest/dev/best-practices.html)
- [Apache Flink Documentation](https://flink.apache.org/docs/stable/)
- [Amazon Timestream Guide](https://docs.aws.amazon.com/timestream/latest/developerguide/what-is-timestream.html)
- [DEA-C01 Exam Guide](https://aws.amazon.com/certification/certified-data-engineer-associate/)

Happy Streaming! 🚀
