# Testing Guide

This guide provides instructions for testing the real-time manufacturing analytics platform.

## Overview

The platform can be tested at multiple levels:
1. **Unit Testing** - Individual components (generator, Flink functions)
2. **Integration Testing** - Component interactions
3. **End-to-End Testing** - Full pipeline verification
4. **Performance Testing** - Throughput and latency validation

## Pre-Deployment Testing

### 1. Validate Terraform Configuration

Before deploying, validate the Terraform configuration:

```bash
cd terraform
terraform init
terraform validate
terraform fmt -check
```

Expected output:
```
Success! The configuration is valid.
```

### 2. Validate Python Code

Check Python syntax and style:

```bash
# Syntax check
python3 -m py_compile src/data_generator/sensor_data_generator.py

# Style check with flake8 (optional)
pip install flake8
flake8 src/data_generator/sensor_data_generator.py --max-line-length=120
```

### 3. Build and Validate Java Code

Compile the Flink application:

```bash
cd src/flink
mvn clean compile
mvn clean package -DskipTests
```

Expected: Build should succeed and create `target/sensor-stream-processor-1.0.0.jar` (~72MB)

## Post-Deployment Testing

After deploying the infrastructure, test each component.

### 1. Test Kinesis Data Stream

Verify the Kinesis stream is active:

```bash
# Get stream name
STREAM_NAME=$(cd terraform && terraform output -raw kinesis_stream_name)

# Check stream status
aws kinesis describe-stream --stream-name $STREAM_NAME

# Expected output: StreamStatus should be "ACTIVE"
```

Test writing to the stream:

```bash
# Send a test record
aws kinesis put-record \
  --stream-name $STREAM_NAME \
  --partition-key "test" \
  --data '{"test":"data","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%S)'"}' \
  --region us-east-1
```

### 2. Test Data Generator

Run the data generator for a short period:

```bash
cd src/data_generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run for 30 seconds
timeout 30 python sensor_data_generator.py \
  --stream-name $STREAM_NAME \
  --region us-east-1 \
  --interval 2.0 \
  --batch-size 5
```

Expected output:
```
Starting sensor data generation...
Stream: manufacturing-analytics-sensor-stream-dev
Interval: 2.0s
Anomaly probability: 5.0%
Batch size: 5
----------------------------------------------------------------------
✓ Batch sent: 5 succeeded, 0 failed
✓ Sent: M001 | temperature | 72.5 celsius | NORMAL
...
```

Verify records in Kinesis:

```bash
# Get shard iterator
SHARD_ITERATOR=$(aws kinesis get-shard-iterator \
  --stream-name $STREAM_NAME \
  --shard-id shardId-000000000000 \
  --shard-iterator-type LATEST \
  --query 'ShardIterator' \
  --output text)

# Get records
aws kinesis get-records --shard-iterator $SHARD_ITERATOR
```

### 3. Test Flink Application

Check Flink application status:

```bash
FLINK_APP_NAME=$(cd terraform && terraform output -raw flink_application_name)

# Describe application
aws kinesisanalyticsv2 describe-application \
  --application-name $FLINK_APP_NAME

# Check status (should be RUNNING)
aws kinesisanalyticsv2 describe-application \
  --application-name $FLINK_APP_NAME \
  --query 'ApplicationDetail.ApplicationStatus'
```

View Flink logs:

```bash
# Tail logs
aws logs tail /aws/kinesis-analytics/$FLINK_APP_NAME --follow

# Search for specific patterns
aws logs filter-log-events \
  --log-group-name /aws/kinesis-analytics/$FLINK_APP_NAME \
  --filter-pattern "ERROR"
```

Check Flink metrics:

```bash
# Get application metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/KinesisAnalytics \
  --metric-name uptime \
  --dimensions Name=Application,Value=$FLINK_APP_NAME \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### 4. Test Timestream Database

Verify database and table exist:

```bash
DATABASE_NAME=$(cd terraform && terraform output -raw timestream_database_name)
TABLE_NAME=$(cd terraform && terraform output -raw timestream_table_name)

# List databases
aws timestream-write list-databases

# Describe table
aws timestream-write describe-table \
  --database-name $DATABASE_NAME \
  --table-name $TABLE_NAME
```

Query data from Timestream:

```bash
# Query recent records
aws timestream-query query \
  --query-string "SELECT * FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" ORDER BY time DESC LIMIT 10"

# Query aggregated metrics
aws timestream-query query \
  --query-string "SELECT machine_id, sensor_type, AVG(measure_value::double) as avg_value FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" WHERE measure_name = 'avg_value' AND time > ago(1h) GROUP BY machine_id, sensor_type"

# Count records
aws timestream-query query \
  --query-string "SELECT COUNT(*) as record_count FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" WHERE time > ago(1h)"
```

### 5. Test CloudWatch Monitoring

View CloudWatch dashboard:

```bash
DASHBOARD_NAME=$(cd terraform && terraform output -raw cloudwatch_dashboard_name)

# Get dashboard
aws cloudwatch get-dashboard --dashboard-name $DASHBOARD_NAME

# List alarms
aws cloudwatch describe-alarms --alarm-name-prefix "manufacturing-analytics"

# Get alarm history
aws cloudwatch describe-alarm-history \
  --alarm-name "manufacturing-analytics-kinesis-iterator-age-dev" \
  --history-item-type StateUpdate \
  --max-records 5
```

## End-to-End Testing

### Full Pipeline Test

This test validates the entire data flow:

1. **Start Data Generator**
   ```bash
   ./scripts/start_data_generator.sh &
   GENERATOR_PID=$!
   ```

2. **Wait for Data to Flow** (2-3 minutes)

3. **Verify Each Stage**
   ```bash
   # Check Kinesis has incoming records
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Kinesis \
     --metric-name IncomingRecords \
     --dimensions Name=StreamName,Value=$STREAM_NAME \
     --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 60 \
     --statistics Sum
   
   # Check Flink is processing
   aws cloudwatch get-metric-statistics \
     --namespace AWS/KinesisAnalytics \
     --metric-name numRecordsInPerSecond \
     --dimensions Name=Application,Value=$FLINK_APP_NAME \
     --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 60 \
     --statistics Average
   
   # Check Timestream has data
   RECORD_COUNT=$(aws timestream-query query \
     --query-string "SELECT COUNT(*) as count FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" WHERE time > ago(5m)" \
     --query 'Rows[0].Data[0].ScalarValue' \
     --output text)
   
   echo "Records in Timestream: $RECORD_COUNT"
   ```

4. **Stop Data Generator**
   ```bash
   kill $GENERATOR_PID
   ```

### Expected Results

- Kinesis should show incoming records (Sum > 0)
- Flink should show processing rate > 0
- Timestream should have records (count > 0)
- All records should arrive within 30-60 seconds

## Performance Testing

### Throughput Test

Measure maximum throughput:

```bash
# Run data generator with high frequency
python src/data_generator/sensor_data_generator.py \
  --stream-name $STREAM_NAME \
  --region us-east-1 \
  --interval 0.1 \
  --batch-size 50
```

Monitor metrics:
- Kinesis: `IncomingRecords`, `IncomingBytes`
- Flink: `numRecordsInPerSecond`, `cpuUtilization`
- Timestream: Write throughput

### Latency Test

Measure end-to-end latency:

1. Generate a record with current timestamp
2. Query Timestream for the record
3. Calculate time difference

```bash
# Generate test record with marker
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)
echo "Generated at: $TIMESTAMP"

# Wait for processing (Flink window is 1 minute)
sleep 90

# Query for recent records
aws timestream-query query \
  --query-string "SELECT * FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" WHERE time > ago(2m) ORDER BY time DESC LIMIT 5"
```

Expected latency: 60-90 seconds (including 1-minute window)

### Fault Tolerance Test

Test recovery from failures:

```bash
# Stop Flink application
aws kinesisanalyticsv2 stop-application \
  --application-name $FLINK_APP_NAME

# Continue sending data
# Data will buffer in Kinesis (up to 24 hours)

# Wait 2 minutes
sleep 120

# Start Flink application
aws kinesisanalyticsv2 start-application \
  --application-name $FLINK_APP_NAME \
  --run-configuration '{}'

# Verify no data loss
# Flink should catch up from checkpoint
```

## Anomaly Detection Testing

Test anomaly detection logic:

```bash
# Run data generator with high anomaly rate
python src/data_generator/sensor_data_generator.py \
  --stream-name $STREAM_NAME \
  --region us-east-1 \
  --anomaly-rate 0.5  # 50% anomalies
```

Query anomaly counts:

```bash
aws timestream-query query \
  --query-string "SELECT machine_id, sensor_type, SUM(measure_value::bigint) as total_anomalies FROM \"$DATABASE_NAME\".\"$TABLE_NAME\" WHERE measure_name = 'anomaly_count' AND time > ago(5m) GROUP BY machine_id, sensor_type ORDER BY total_anomalies DESC"
```

## Troubleshooting Tests

### Test 1: No Data in Kinesis

```bash
# Check stream status
aws kinesis describe-stream --stream-name $STREAM_NAME

# Verify IAM permissions
aws iam get-role-policy \
  --role-name manufacturing-analytics-data-generator-role-dev \
  --policy-name kinesis-write-policy

# Test write permission
aws kinesis put-record \
  --stream-name $STREAM_NAME \
  --partition-key "test" \
  --data "dGVzdA==" \
  --region us-east-1
```

### Test 2: Flink Not Processing

```bash
# Check Flink status
aws kinesisanalyticsv2 describe-application \
  --application-name $FLINK_APP_NAME \
  --query 'ApplicationDetail.{Status:ApplicationStatus,StatusMessage:LastUpdateTimestamp}'

# Check for errors in logs
aws logs filter-log-events \
  --log-group-name /aws/kinesis-analytics/$FLINK_APP_NAME \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s) - 3600))000

# Verify JAR exists in S3
S3_BUCKET=$(cd terraform && terraform output -raw s3_bucket_name)
aws s3 ls s3://$S3_BUCKET/flink-app.jar
```

### Test 3: No Data in Timestream

```bash
# Check Timestream table
aws timestream-write describe-table \
  --database-name $DATABASE_NAME \
  --table-name $TABLE_NAME

# Verify IAM permissions
aws iam get-role-policy \
  --role-name manufacturing-analytics-flink-role-dev \
  --policy-name timestream-write-policy

# Check for rejected records
aws s3 ls s3://$(cd terraform && terraform output -raw s3_bucket_name | grep rejected)/
```

## Automated Testing

### Using Makefile

The provided Makefile includes test commands:

```bash
# Build and validate
make build
make validate

# Deploy and test
make deploy
make start-flink
make start-generator

# Verify
make logs     # Check processing logs
make query    # Query Timestream

# Cleanup
make destroy
```

## Test Checklist

Before considering the deployment successful:

- [ ] Terraform configuration validates without errors
- [ ] Python code syntax is valid
- [ ] Java code compiles and produces JAR
- [ ] Kinesis stream is active
- [ ] Data generator successfully writes to Kinesis
- [ ] Flink application status is RUNNING
- [ ] Flink processes records (check metrics)
- [ ] Timestream receives aggregated data
- [ ] CloudWatch dashboard displays metrics
- [ ] CloudWatch alarms are configured
- [ ] Grafana can query Timestream
- [ ] End-to-end latency is acceptable
- [ ] No errors in Flink logs
- [ ] Fault tolerance works (checkpoint recovery)
- [ ] Anomaly detection flags anomalous values

## Continuous Testing

For production environments:

1. Set up automated testing pipeline
2. Run smoke tests after each deployment
3. Monitor key metrics continuously
4. Set up alerts for test failures
5. Perform regular load testing
6. Test disaster recovery procedures quarterly

## Test Data Cleanup

After testing:

```bash
# Stop data generator (Ctrl+C or kill process)

# Stop Flink application
aws kinesisanalyticsv2 stop-application --application-name $FLINK_APP_NAME

# Optional: Clear Timestream data (wait for retention period)
# Or delete and recreate the table

# Destroy infrastructure
cd terraform
terraform destroy
```

## Additional Resources

- [AWS Kinesis Testing Best Practices](https://docs.aws.amazon.com/streams/latest/dev/kinesis-record-processor-implementation-app-java.html)
- [Flink Testing Documentation](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/testing/)
- [Timestream Query Examples](https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.html)
