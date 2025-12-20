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
