# Real-Time Manufacturing Sensor Streaming

A comprehensive, production-ready solution for real-time analytics of manufacturing sensor data using AWS Kinesis Data Streams, Apache Flink, Amazon Timestream, and Grafana.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

This repository provides a complete Infrastructure as Code (IaC) solution for building a low-latency, scalable real-time analytics pipeline for manufacturing sensor data. The solution is designed with maximum modularity, reusability, and best practices in mind.

### Architecture

```
Sensors → Kinesis Data Streams → Flink Processing → Timestream → Grafana
```

**Key Features:**
- ⚡ Real-time data ingestion with millisecond latency
- 🔄 Stream processing with Apache Flink
- 📊 Time-series storage with Amazon Timestream
- 📈 Interactive dashboards with Grafana
- 🏗️ Fully automated infrastructure deployment
- 🔒 Enterprise-grade security
- 📦 Highly modular and reusable components

## 📚 Documentation

### Quick Start
1. **Complete Tutorial** - [100-Step Tutorial from Novice to Expert](docs/TUTORIAL_MASTER.md)
2. **Beginner Guide** - See [docs/beginner/](docs/beginner/)
3. **Advanced Topics** - See [docs/advanced/](docs/advanced/)

### Key Documentation Files
- [Architecture Overview](docs/beginner/12-data-flow.md)
- [Deployment Guide](docs/intermediate/27-deploy-vpc.md)
- [Configuration Guide](docs/beginner/13-configuration.md)
- [Troubleshooting](docs/beginner/24-troubleshooting.md)

## 🗂️ Repository Structure

```
.
├── config/                     # Configuration files
│   ├── dev/                   # Development environment config
│   ├── staging/               # Staging environment config
│   └── prod/                  # Production environment config
├── docs/                      # Documentation
│   ├── TUTORIAL_MASTER.md    # Complete 100-step tutorial
│   ├── beginner/             # Beginner tutorials (Steps 1-25)
│   ├── intermediate/         # Intermediate guides (Steps 26-60)
│   ├── advanced/             # Advanced topics (Steps 61-85)
│   ├── expert/               # Expert level (Steps 86-100)
│   └── diagrams/             # Architecture diagrams
├── python/                    # Python application code
│   ├── src/
│   │   ├── ingestion/        # Data ingestion modules
│   │   ├── processing/       # Data processing utilities
│   │   ├── storage/          # Timestream client
│   │   ├── monitoring/       # Monitoring utilities
│   │   └── utils/            # Common utilities
│   ├── tests/
│   │   ├── unit/             # Unit tests
│   │   ├── integration/      # Integration tests
│   │   └── e2e/              # End-to-end tests
│   └── requirements.txt      # Python dependencies
├── terraform/                 # Infrastructure as Code
│   ├── modules/
│   │   ├── kinesis/          # Kinesis Data Streams module
│   │   ├── flink/            # Flink application module
│   │   ├── timestream/       # Timestream module
│   │   ├── vpc/              # VPC and networking module
│   │   ├── iam/              # IAM roles and policies
│   │   ├── s3/               # S3 buckets module
│   │   ├── cloudwatch/       # CloudWatch monitoring
│   │   └── grafana/          # Grafana deployment
│   └── environments/
│       ├── dev/              # Development environment
│       ├── staging/          # Staging environment
│       └── prod/             # Production environment
├── scripts/                   # Automation scripts
│   ├── setup/                # Environment setup scripts
│   ├── deployment/           # Deployment automation
│   └── testing/              # Testing utilities
├── examples/                  # Example code and tutorials
│   ├── python/               # Python examples
│   └── terraform/            # Terraform examples
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- AWS Account with appropriate permissions
- Python 3.9 or later
- Terraform 1.0 or later
- AWS CLI v2
- Git

### Installation

1. **Clone the repository**
# Real-Time Manufacturing Analytics Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple.svg)](https://www.terraform.io/)

A production-ready, real-time analytics platform for manufacturing sensor data built on AWS. This solution demonstrates best practices for streaming data architecture following AWS Data Engineer Associate (DEA-C01) certification guidelines.

## 🎯 Overview

This platform ingests, processes, and visualizes manufacturing sensor data in real-time with:
- **Low-latency data ingestion** with Amazon Kinesis Data Streams
- **Real-time stream processing** using Amazon Managed Service for Apache Flink
- **Time-series data storage** in Amazon Timestream
- **Live operational dashboards** with Grafana
- **Enterprise-grade security** with IAM least privilege and KMS encryption
- **Comprehensive monitoring** with CloudWatch metrics and alarms
- **Fault tolerance** through checkpointing and auto-recovery
- **Infrastructure as Code** with Terraform

## 🏗️ Architecture

```
Manufacturing Sensors → Kinesis Data Streams → Flink Processing → Timestream → Grafana
                              ↓                       ↓               ↓
                         CloudWatch ←────────────────┴───────────────┘
```

**Key Features:**
- 📊 Real-time windowed aggregations (avg, min, max)
- 🚨 Automated anomaly detection and alerting
- 🔒 End-to-end encryption (at rest and in transit)
- 📈 Auto-scaling based on throughput
- 💾 Data lifecycle management (memory → magnetic storage)
- 🛡️ IAM least privilege security model
- 📉 Cost-optimized with right-sizing and lifecycle policies

See [Architecture Documentation](docs/ARCHITECTURE.md) for detailed design.

## 📋 Prerequisites

- **AWS Account** with appropriate permissions
- **Terraform** >= 1.0
- **AWS CLI** >= 2.0 (configured)
- **Maven** >= 3.6
- **Java** >= 11
- **Python** >= 3.8
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream.git
cd real-time-manufacturing-sensor-streaming-kinesis-flink-timestream
```

2. **Set up Python environment**
```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
```

4. **Initialize Terraform**
```bash
cd terraform/environments/dev
terraform init
```

5. **Deploy infrastructure**
```bash
terraform plan
terraform apply
```

For detailed step-by-step instructions, see the [Complete Tutorial](docs/TUTORIAL_MASTER.md).

## 💻 Usage Examples

### Generate and Send Sensor Data

```python
from python.src.ingestion import DataGenerator, KinesisProducer

# Initialize data generator
generator = DataGenerator(
    num_machines=5,
    sensors_per_machine=4,
    location="Factory-A"
)

# Initialize Kinesis producer
producer = KinesisProducer(
    stream_name="manufacturing-sensor-stream",
    region_name="us-east-1"
)

# Generate and send data
readings = generator.generate_batch()
producer.put_sensor_readings(readings)
```

### Query Timestream Data

```python
from python.src.storage import TimestreamClient

# Initialize client
client = TimestreamClient(
    database_name="manufacturing_db",
    table_name="sensor_data"
)

# Query latest readings
results = client.query_latest_by_sensor("SENSOR-001", limit=10)
print(results)
```

### Process Data with Flink

See [docs/intermediate/37-flink-processing.md](docs/intermediate/37-flink-processing.md) for Flink application examples.

## 🏗️ Infrastructure Modules

The solution uses highly modular Terraform modules:

| Module | Purpose | Location |
|--------|---------|----------|
| **kinesis** | Kinesis Data Streams | `terraform/modules/kinesis/` |
| **timestream** | Timestream database & table | `terraform/modules/timestream/` |
| **flink** | Managed Flink application | `terraform/modules/flink/` |
| **vpc** | VPC and networking | `terraform/modules/vpc/` |
| **iam** | IAM roles and policies | `terraform/modules/iam/` |
| **s3** | S3 buckets | `terraform/modules/s3/` |
| **cloudwatch** | Monitoring and alerting | `terraform/modules/cloudwatch/` |
| **grafana** | Grafana visualization | `terraform/modules/grafana/` |

Each module is:
- ✅ Fully reusable
- ✅ Well-documented
- ✅ Configurable via variables
- ✅ Production-ready

## 🔧 Configuration

Configuration is managed via JSON files in the `config/` directory:

- **Development**: `config/dev/config.json`
- **Staging**: `config/staging/config.json`
- **Production**: `config/prod/config.json`

Environment variables can override configuration values:
```bash
export AWS_REGION=us-east-1
export KINESIS_STREAM_NAME=my-stream
export TIMESTREAM_DATABASE=my-database
```

See [Configuration Guide](docs/beginner/13-configuration.md) for details.

## 🧪 Testing

### Run Unit Tests
```bash
cd python
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Run End-to-End Tests
```bash
pytest tests/e2e/
```

## 📊 Monitoring

The solution includes comprehensive monitoring:
- CloudWatch metrics for all services
- Custom application metrics
- Alarms for critical conditions
- Grafana dashboards for visualization

See [Monitoring Guide](docs/beginner/20-monitoring-basics.md).

## 🔒 Security

Security best practices are built-in:
- Encryption at rest and in transit
- Least privilege IAM policies
- VPC isolation
- Security groups and NACLs
- Secrets management

See [Security Guide](docs/beginner/19-security-basics.md).

## 💰 Cost Optimization

Estimated monthly costs (vary by usage):
- **Development**: ~$50-100/month
- **Production**: ~$500-1000/month

See [Cost Estimation Guide](docs/beginner/18-cost-estimation.md).

## 🤝 Contributing

Contributions are welcome! Please see:
- [Contributing Guide](docs/expert/98-contributing.md)
- [Code of Conduct](CONTRIBUTING.md)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Troubleshooting**: [docs/beginner/24-troubleshooting.md](docs/beginner/24-troubleshooting.md)
- **Issues**: [GitHub Issues](https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream/issues)

## 🎓 Learning Path

1. **Beginner** (Steps 1-25): Start with basics, understand concepts
2. **Intermediate** (Steps 26-60): Deploy and configure the solution
3. **Advanced** (Steps 61-85): Optimize and add advanced features
4. **Expert** (Steps 86-100): Enterprise scale and operations

See the [Complete Tutorial](docs/TUTORIAL_MASTER.md) for the full learning path.

## 🌟 Features by Version

### v1.0.0 (Current)
- ✅ Complete infrastructure modules
- ✅ Python data generator and producer
- ✅ Timestream client
- ✅ Configuration management
- ✅ Comprehensive documentation
- ✅ 100-step tutorial

### Roadmap
- [ ] Flink application implementation
- [ ] Grafana dashboard templates
- [ ] CI/CD pipeline
- [ ] Multi-region support
- [ ] ML integration

## 📞 Contact

For questions or support:
- Email: support@example.com
- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream/issues)

---

**Built with ❤️ for the manufacturing industry**
### 2. Configure Variables

Create `terraform/terraform.tfvars`:

```hcl
aws_region          = "us-east-1"
environment         = "dev"
project_name        = "manufacturing-analytics"
kinesis_shard_count = 2
alarm_email         = "your-email@example.com"  # Optional
```

### 3. Build and Deploy

```bash
# Build Flink application
./scripts/build_flink_app.sh

# Deploy infrastructure
./scripts/deploy_infrastructure.sh

# Upload Flink JAR to S3
./scripts/upload_flink_jar.sh

# Start Flink application (via AWS Console or CLI)
```

### 4. Generate Data

```bash
# Start sensor data generator
./scripts/start_data_generator.sh
```

### 5. Visualize

- **CloudWatch Dashboard**: View real-time metrics
- **Grafana**: Import dashboard from `grafana/dashboard.json`
- **Timestream Queries**: Query aggregated metrics directly

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 📁 Project Structure

```
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Provider configuration
│   ├── variables.tf           # Input variables
│   ├── outputs.tf             # Output values
│   ├── kinesis.tf             # Kinesis Data Streams
│   ├── flink.tf               # Managed Flink application
│   ├── timestream.tf          # Timestream database
│   ├── iam.tf                 # IAM roles and policies
│   ├── s3.tf                  # S3 buckets
│   └── monitoring.tf          # CloudWatch monitoring
│
├── src/
│   ├── flink/                 # Flink application (Java)
│   │   ├── pom.xml           # Maven configuration
│   │   └── src/main/java/    # Java source code
│   │       └── com/manufacturing/analytics/
│   │           ├── SensorStreamProcessor.java
│   │           └── TimestreamSink.java
│   │
│   └── data_generator/        # Sensor data generator (Python)
│       ├── sensor_data_generator.py
│       └── requirements.txt
│
├── grafana/                   # Grafana configuration
│   ├── dashboard.json        # Pre-built dashboard
│   └── datasource.yaml       # Timestream data source
│
├── scripts/                   # Deployment scripts
│   ├── build_flink_app.sh
│   ├── deploy_infrastructure.sh
│   ├── upload_flink_jar.sh
│   └── start_data_generator.sh
│
└── docs/                      # Documentation
    ├── ARCHITECTURE.md       # Architecture details
    └── DEPLOYMENT.md         # Deployment guide
```

## 🔐 Security Features

### Encryption
- **At Rest**: KMS encryption for Kinesis, Timestream, S3, SNS
- **In Transit**: TLS for all service communications
- **Key Management**: Automatic key rotation, 10-day deletion window

### IAM Least Privilege
- Separate roles for Flink, data generator, and Grafana
- Resource-level permissions (specific streams, tables, buckets)
- No wildcard permissions

### Data Protection
- S3 public access blocked
- Versioning enabled on critical buckets
- Rejected data lifecycle policies

## 📊 Monitoring & Alerting

### CloudWatch Dashboards
- Kinesis stream metrics (throughput, iterator age)
- Flink application metrics (uptime, checkpoints, CPU)
- Custom visualizations for key KPIs

### CloudWatch Alarms
- High iterator age (processing lag)
- No incoming records (pipeline failure)
- Flink application downtime
- Checkpoint failures
- SNS notifications to email/SMS

## 🎛️ Data Pipeline

### Data Generator
Simulates manufacturing equipment:
- 5 machines (M001-M005)
- 5 sensor types: temperature, pressure, vibration, power consumption, cycle time
- Realistic value ranges
- Configurable anomaly injection (default 5%)

### Stream Processing
Flink application:
- Reads from Kinesis with watermarks
- 1-minute tumbling windows
- Aggregations: avg, min, max, count, anomaly_count
- Groups by machine_id and sensor_type

### Data Storage
Timestream table:
- Dimensions: machine_id, sensor_type, location, production_line
- Measures: avg_value, min_value, max_value, record_count, anomaly_count
- Memory store: 24 hours (fast queries)
- Magnetic store: 90 days (cost-effective)

### Visualization
Grafana dashboards:
- Temperature trends by machine
- Pressure monitoring
- Vibration levels
- Power consumption
- Anomaly detection statistics
- Production line performance

## 🔧 Configuration

### Scaling

Increase throughput by adjusting shards:

```hcl
kinesis_shard_count = 4  # Increase from 2 to 4
```

Flink parallelism automatically adjusts.

### Retention

Modify data retention periods:

```hcl
timestream_memory_retention_hours  = 48
timestream_magnetic_retention_days = 180
```

### Cost Optimization

- Run Flink only during business hours
- Reduce data generation frequency
- Optimize query patterns
- Use lifecycle policies

## 🧪 Testing

The system can be tested end-to-end:

1. Start data generator
2. Verify Kinesis receives data (CloudWatch)
3. Check Flink logs for processing
4. Query Timestream for aggregated data
5. View live metrics in Grafana

## 📈 Performance

- **Ingestion**: 1000+ records/second per shard
- **Processing Latency**: < 10 seconds (including windowing)
- **Query Performance**: Sub-second for recent data
- **Fault Tolerance**: Checkpoint every 60 seconds

## 💰 Cost Estimation

Approximate monthly costs (us-east-1):
- Kinesis Data Streams: ~$36
- Managed Flink: ~$140
- Timestream: ~$150
- Other services: ~$15
- **Total**: ~$341/month

See [Deployment Guide](docs/DEPLOYMENT.md) for cost optimization strategies.

## 🛠️ Troubleshooting

### Common Issues

**Flink application fails to start**
- Check CloudWatch logs
- Verify JAR uploaded to S3
- Confirm IAM permissions

**No data in Timestream**
- Verify data generator is running
- Check Kinesis metrics
- Review Flink logs

**High iterator age**
- Increase Kinesis shards
- Check Flink resource usage
- Review checkpoint duration

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed troubleshooting.

## 🧹 Cleanup

Remove all resources:

```bash
cd terraform
terraform destroy
```

**Warning**: This deletes all data and cannot be undone.

## 📚 DEA-C01 Best Practices

This project demonstrates:
- ✅ Streaming data ingestion with Kinesis
- ✅ Real-time processing with managed Flink
- ✅ Purpose-built databases (Timestream for time-series)
- ✅ Security best practices (encryption, IAM least privilege)
- ✅ Monitoring and observability
- ✅ Fault tolerance and disaster recovery
- ✅ Cost optimization strategies
- ✅ Infrastructure as Code
- ✅ Automated deployments
- ✅ Data lifecycle management

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with AWS services:
- Amazon Kinesis Data Streams
- Amazon Managed Service for Apache Flink
- Amazon Timestream
- Amazon CloudWatch
- AWS IAM
- AWS KMS
- Amazon S3
- Amazon SNS

## 📞 Support

For issues and questions:
- Open a GitHub issue
- Check the [documentation](docs/)
- Review AWS service documentation

## 🗺️ Roadmap

Future enhancements:
- [ ] Machine learning-based anomaly detection
- [ ] Multi-region deployment
- [ ] Real-time alerting via PagerDuty/Slack
- [ ] Data quality monitoring
- [ ] Custom metric aggregations
- [ ] Integration with AWS IoT Core
- [ ] API for custom integrations
- [ ] Additional dashboard templates
