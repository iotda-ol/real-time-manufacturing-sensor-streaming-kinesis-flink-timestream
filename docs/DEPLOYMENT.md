# Deployment Guide

This guide walks through deploying the real-time manufacturing analytics platform on AWS.

## Prerequisites

### Required Tools
- **Terraform** >= 1.0 (for infrastructure provisioning)
- **AWS CLI** >= 2.0 (configured with appropriate credentials)
- **Maven** >= 3.6 (for building Flink application)
- **Java** >= 11 (for Flink application)
- **Python** >= 3.8 (for data generator)
- **Git** (for cloning the repository)

### AWS Requirements
- AWS Account with sufficient permissions
- AWS credentials configured (`aws configure`)
- Permissions required:
  - Kinesis Data Streams (create, manage)
  - Kinesis Analytics v2 (create, manage)
  - Timestream (create, manage)
  - S3 (create buckets, upload objects)
  - IAM (create roles and policies)
  - CloudWatch (create dashboards, alarms)
  - KMS (create and manage keys)
  - SNS (create topics)

## Deployment Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream.git
cd real-time-manufacturing-sensor-streaming-kinesis-flink-timestream
```

### Step 2: Configure Variables

Edit `terraform/variables.tf` or create a `terraform.tfvars` file:

```hcl
# terraform/terraform.tfvars
aws_region                         = "us-east-1"
environment                        = "dev"
project_name                       = "manufacturing-analytics"
kinesis_shard_count                = 2
kinesis_retention_hours            = 24
timestream_memory_retention_hours  = 24
timestream_magnetic_retention_days = 90
enable_enhanced_monitoring         = true
alarm_email                        = "your-email@example.com"  # Optional
```

### Step 3: Build the Flink Application

```bash
cd src/flink
mvn clean package
```

This creates `target/sensor-stream-processor-1.0.0.jar`.

Or use the provided script:

```bash
./scripts/build_flink_app.sh
```

### Step 4: Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Or use the provided script:

```bash
./scripts/deploy_infrastructure.sh
```

This will create:
- Kinesis Data Stream
- Amazon Timestream database and table
- Amazon Managed Service for Apache Flink application (configured)
- S3 buckets for artifacts and rejected data
- IAM roles and policies
- KMS keys for encryption
- CloudWatch dashboard and alarms
- SNS topic for alerts

The deployment takes approximately 5-10 minutes.

### Step 5: Upload Flink Application JAR

After the infrastructure is deployed, upload the Flink application JAR to S3:

```bash
# Get the S3 bucket name from Terraform outputs
S3_BUCKET=$(terraform output -raw s3_bucket_name)

# Upload the JAR
aws s3 cp ../src/flink/target/sensor-stream-processor-1.0.0.jar \
  s3://${S3_BUCKET}/flink-app.jar
```

Or use the provided script:

```bash
./scripts/upload_flink_jar.sh
```

### Step 6: Start the Flink Application

Start the Flink application from the AWS Console or using AWS CLI:

```bash
FLINK_APP_NAME=$(terraform output -raw flink_application_name)

aws kinesisanalyticsv2 start-application \
  --application-name ${FLINK_APP_NAME} \
  --run-configuration '{}'
```

Wait for the application status to change to "RUNNING" (takes 2-3 minutes):

```bash
aws kinesisanalyticsv2 describe-application \
  --application-name ${FLINK_APP_NAME} \
  --query 'ApplicationDetail.ApplicationStatus'
```

### Step 7: Start Data Generator

Generate sensor data and send it to Kinesis:

```bash
cd src/data_generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run data generator
STREAM_NAME=$(cd ../../terraform && terraform output -raw kinesis_stream_name)
python sensor_data_generator.py --stream-name ${STREAM_NAME} --region us-east-1
```

Or use the provided script:

```bash
./scripts/start_data_generator.sh
```

You should see output like:
```
✓ Batch sent: 10 succeeded, 0 failed
✓ Sent: M001 | temperature | 72.5 celsius | NORMAL
✓ Sent: M002 | pressure | 105.3 psi | NORMAL
✓ Sent: M003 | vibration | 0.35 mm/s | ANOMALY
...
```

### Step 8: Monitor the Pipeline

#### CloudWatch Dashboard

View the CloudWatch dashboard:

```bash
DASHBOARD_NAME=$(cd terraform && terraform output -raw cloudwatch_dashboard_name)
echo "Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${DASHBOARD_NAME}"
```

#### View Logs

Check Flink application logs:

```bash
aws logs tail /aws/kinesis-analytics/manufacturing-analytics-sensor-processor-dev \
  --follow \
  --format short
```

#### Query Timestream

Verify data is being written to Timestream:

```bash
DATABASE_NAME=$(cd terraform && terraform output -raw timestream_database_name)
TABLE_NAME=$(cd terraform && terraform output -raw timestream_table_name)

aws timestream-query query \
  --query-string "SELECT * FROM \"${DATABASE_NAME}\".\"${TABLE_NAME}\" ORDER BY time DESC LIMIT 10"
```

### Step 9: Set Up Grafana (Optional)

#### Option A: Amazon Managed Grafana

1. Create a workspace in Amazon Managed Grafana
2. Configure the Timestream data source using `grafana/datasource.yaml`
3. Import the dashboard from `grafana/dashboard.json`

#### Option B: Self-Hosted Grafana

1. Install Grafana on EC2 or locally
2. Install the Timestream data source plugin:
   ```bash
   grafana-cli plugins install grafana-timestream-datasource
   ```
3. Configure data source with IAM role or access keys
4. Import the dashboard from `grafana/dashboard.json`

### Step 10: Verify End-to-End

1. Data generator is sending records to Kinesis ✓
2. Kinesis stream is receiving data (check CloudWatch metrics) ✓
3. Flink application is processing data (check logs and metrics) ✓
4. Timestream is storing aggregated metrics (query the table) ✓
5. Grafana is displaying live dashboards ✓

## Configuration Options

### Adjusting Throughput

To handle higher data volumes, increase Kinesis shards:

```hcl
# terraform.tfvars
kinesis_shard_count = 4  # Increase from 2 to 4
```

Then apply the change:

```bash
cd terraform
terraform apply
```

Flink parallelism will automatically adjust.

### Modifying Retention Periods

Adjust data retention in Timestream:

```hcl
# terraform.tfvars
timestream_memory_retention_hours  = 48   # Increase to 2 days
timestream_magnetic_retention_days = 180  # Increase to 6 months
```

### Customizing Alarms

Modify alarm thresholds in `terraform/monitoring.tf`:

```hcl
# Example: Change iterator age threshold
threshold = "120000"  # 2 minutes instead of 1
```

## Troubleshooting

### Flink Application Fails to Start

1. Check CloudWatch logs for errors
2. Verify JAR was uploaded to S3
3. Ensure IAM role has required permissions
4. Check Kinesis stream exists and is active

### No Data in Timestream

1. Verify data generator is running
2. Check Kinesis stream has incoming records (CloudWatch)
3. Review Flink application logs for errors
4. Verify Timestream table exists
5. Check IAM permissions for Timestream writes

### High Iterator Age

This indicates processing lag:

1. Increase Kinesis shards
2. Check Flink application CPU/memory usage
3. Review checkpoint duration metrics
4. Scale Flink parallelism

### Checkpoint Failures

1. Check Flink logs for specific errors
2. Verify sufficient resources (CPU/memory)
3. Review checkpoint configuration
4. Check state backend storage

## Cleanup

To remove all resources and avoid ongoing charges:

```bash
cd terraform
terraform destroy
```

This will delete:
- All AWS resources created by Terraform
- Data in Kinesis, Timestream, and S3
- CloudWatch dashboards and alarms

**Note**: KMS keys will be scheduled for deletion (10-day window) and cannot be recovered.

## Cost Estimation

Approximate monthly costs (us-east-1, as of 2024):

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| Kinesis Data Streams | 2 shards, 24h retention | $36 |
| Managed Flink | 1 KPU running continuously | $140 |
| Timestream | 100M writes, 10M queries | $150 |
| S3 | 1GB storage, minimal requests | $1 |
| CloudWatch | Standard metrics + logs | $10 |
| KMS | 4 keys, minimal requests | $4 |
| **Total** | | **~$341/month** |

Costs can be reduced by:
- Running Flink only during business hours
- Reducing data generation frequency
- Optimizing Timestream queries
- Using shorter retention periods

## Next Steps

- Customize Grafana dashboards for your metrics
- Add more sensor types or machines
- Implement custom anomaly detection algorithms
- Set up automated alerts and notifications
- Integrate with existing monitoring systems
- Implement data quality checks
- Add data validation and cleansing logic
