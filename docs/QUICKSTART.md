# Quick Start Guide

Get up and running with the manufacturing sensor streaming solution in 15 minutes.

## Prerequisites

Before you begin, ensure you have:
- ✅ AWS Account with admin access
- ✅ Python 3.9+ installed
- ✅ Git installed
- ✅ Basic command line knowledge

## Step 1: Clone the Repository (2 minutes)

```bash
git clone https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream.git
cd real-time-manufacturing-sensor-streaming-kinesis-flink-timestream
```

## Step 2: Setup Development Environment (3 minutes)

Run the automated setup script:

```bash
bash scripts/setup/setup_dev_environment.sh
```

This script will:
- Check for required tools
- Create Python virtual environment
- Install dependencies
- Verify AWS credentials

## Step 3: Configure AWS (2 minutes)

If not already configured:

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Output format (e.g., `json`)

## Step 4: Try the Hello World Example (2 minutes)

Test that everything works:

```bash
python3 examples/python/hello_world.py
```

Expected output:
```
============================================================
Hello World - Manufacturing Sensor Streaming
============================================================

Initialized generator with 4 sensors

Generating 5 sensor readings...

Reading 1:
  Sensor ID: MACHINE-001-TEMPERATURE-01
  Type: temperature
  Value: 25.5 celsius
  ...
```

## Step 5: Review Configuration (2 minutes)

Edit the development configuration:

```bash
# View current config
cat config/dev/config.json

# Edit if needed
nano config/dev/config.json
```

Key settings:
- `kinesis.stream_name` - Kinesis stream name
- `timestream.database` - Database name
- `aws.region` - AWS region

## Step 6: Deploy Infrastructure (Optional, 4 minutes)

⚠️ **Warning**: This will create AWS resources and incur costs (~$1-2/day for dev environment)

```bash
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Deploy (when ready)
terraform apply
```

Resources created:
- VPC with public/private subnets
- Kinesis Data Stream (2 shards)
- Timestream database and table
- S3 buckets
- IAM roles

## What's Next?

### Option A: Learn More (Beginner Path)
Follow the complete tutorial:
```bash
cat docs/TUTORIAL_MASTER.md
```

Start with beginner steps:
1. [Introduction to Real-Time Analytics](docs/beginner/01-introduction.md)
2. [Repository Structure](docs/beginner/05-repository-structure.md)

### Option B: Start Coding (Intermediate Path)
Run the end-to-end example (requires deployed infrastructure):
```bash
python3 examples/python/e2e_ingestion_example.py \
  --stream-name manufacturing-sensor-stream-dev \
  --num-records 100
```

### Option C: Explore Modules (Advanced Path)
Review the modular architecture:
- **Python modules**: `python/src/`
- **Terraform modules**: `terraform/modules/`
- **Configuration**: `config/`

## Troubleshooting

### Python Import Errors
```bash
# Ensure you're in the project root
cd /path/to/project

# Run examples from project root
python3 examples/python/hello_world.py
```

### AWS Credentials Not Found
```bash
# Check credentials
aws sts get-caller-identity

# If not working, reconfigure
aws configure
```

### Terraform Errors
```bash
# Ensure you're in the right directory
cd terraform/environments/dev

# Re-initialize if needed
terraform init -upgrade
```

## Quick Commands Reference

```bash
# Python Examples
python3 examples/python/hello_world.py
python3 examples/python/e2e_ingestion_example.py --help

# Terraform
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
terraform destroy  # Clean up

# Testing
cd python
source venv/bin/activate
pytest tests/unit/ -v

# Documentation
cat docs/TUTORIAL_MASTER.md
ls docs/beginner/
```

## Cost Estimate

**Development Environment** (per day):
- Kinesis (2 shards): ~$0.50
- Timestream (minimal data): ~$0.30
- S3 storage: ~$0.01
- VPC/NAT Gateway: ~$1.20
- **Total**: ~$2.00/day or ~$60/month

💡 **Tip**: Destroy resources when not in use:
```bash
cd terraform/environments/dev
terraform destroy
```

## Getting Help

1. **Check Documentation**: `docs/`
2. **Review Examples**: `examples/`
3. **Read Troubleshooting**: `docs/beginner/24-troubleshooting.md` (coming soon)
4. **Open Issue**: [GitHub Issues](https://github.com/iotda-ol/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream/issues)

## Success Checklist

After completing this guide, you should have:
- [x] Repository cloned
- [x] Development environment set up
- [x] AWS credentials configured
- [x] Hello world example working
- [x] Understanding of project structure
- [ ] (Optional) Infrastructure deployed
- [ ] (Optional) E2E example tested

## Next Steps by Role

### **Developers**
→ Start coding with `python/src/` modules
→ Review `docs/intermediate/` for deployment guides

### **DevOps/SRE**
→ Explore `terraform/modules/` for infrastructure
→ Review `scripts/deployment/` for automation

### **Data Engineers**
→ Study data flow in `docs/beginner/12-data-flow.md`
→ Experiment with data processing in `python/src/processing/`

### **Architects**
→ Review architecture in `docs/diagrams/`
→ Explore advanced topics in `docs/advanced/`

---

**Time to Production-Ready**: Follow the 100-step tutorial to go from novice to expert!

🎯 **Your Progress**: Completed Quick Start (Steps 1-6 of 100)
