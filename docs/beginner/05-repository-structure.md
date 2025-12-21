# Step 5: Repository Structure

## Understanding the Directory Layout

This repository is organized for maximum modularity and reusability. Each directory serves a specific purpose.

## Top-Level Structure

```
real-time-manufacturing-sensor-streaming/
├── config/          # Configuration files
├── docs/            # Documentation
├── python/          # Python application code
├── terraform/       # Infrastructure as Code
├── scripts/         # Automation scripts
├── examples/        # Example code
├── .gitignore       # Git ignore rules
└── README.md        # Project overview
```

## Configuration Directory (`config/`)

Environment-specific configuration files:

```
config/
├── dev/
│   └── config.json       # Development settings
├── staging/
│   └── config.json       # Staging settings
└── prod/
    └── config.json       # Production settings
```

**Purpose**: Separates configuration from code, enabling easy environment switching.

## Documentation Directory (`docs/`)

Comprehensive documentation organized by skill level:

```
docs/
├── TUTORIAL_MASTER.md    # 100-step tutorial
├── beginner/             # Steps 1-25
├── intermediate/         # Steps 26-60
├── advanced/             # Steps 61-85
├── expert/               # Steps 86-100
└── diagrams/             # Architecture diagrams
```

**Purpose**: Progressive learning path from novice to expert.

## Python Directory (`python/`)

All Python application code:

```
python/
├── src/
│   ├── ingestion/        # Data ingestion modules
│   │   ├── data_generator.py
│   │   └── kinesis_producer.py
│   ├── processing/       # Data processing
│   │   ├── data_processor.py
│   │   └── data_transformer.py
│   ├── storage/          # Storage clients
│   │   └── timestream_client.py
│   ├── monitoring/       # Monitoring utilities
│   └── utils/            # Common utilities
│       ├── config_manager.py
│       └── logger.py
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
└── requirements.txt      # Python dependencies
```

**Purpose**: Modular, reusable Python packages for all functionality.

## Terraform Directory (`terraform/`)

Infrastructure as Code organized by modules and environments:

```
terraform/
├── modules/
│   ├── kinesis/          # Kinesis module
│   ├── flink/            # Flink module
│   ├── timestream/       # Timestream module
│   ├── vpc/              # VPC module
│   ├── iam/              # IAM module
│   ├── s3/               # S3 module
│   ├── cloudwatch/       # Monitoring module
│   └── grafana/          # Grafana module
└── environments/
    ├── dev/              # Dev environment config
    ├── staging/          # Staging environment config
    └── prod/             # Prod environment config
```

**Purpose**: Reusable infrastructure modules for consistent deployments.

## Scripts Directory (`scripts/`)

Automation scripts for common tasks:

```
scripts/
├── setup/
│   └── setup_dev_environment.sh    # Environment setup
├── deployment/
│   └── deploy.sh                    # Deployment automation
└── testing/
    └── run_tests.sh                 # Test automation
```

**Purpose**: Automate repetitive tasks and workflows.

## Examples Directory (`examples/`)

Sample code and tutorials:

```
examples/
├── python/
│   ├── hello_world.py              # Basic example
│   └── e2e_ingestion_example.py    # Complete example
└── terraform/
    └── simple_deployment/           # Minimal deployment
```

**Purpose**: Learn by example with working code samples.

## Key Design Principles

### 1. **Separation of Concerns**
- Infrastructure (Terraform) separate from application code (Python)
- Configuration separate from code
- Tests separate from source code

### 2. **Modularity**
- Each Terraform module is self-contained
- Each Python module has a single responsibility
- Easy to reuse components in different contexts

### 3. **Environment Isolation**
- Separate configurations for dev, staging, prod
- No hard-coded values
- Environment variables for overrides

### 4. **Progressive Disclosure**
- Documentation organized by skill level
- Examples from simple to complex
- Clear learning path

## Navigating the Repository

### For Beginners
Start with:
1. `README.md` - Overview
2. `docs/TUTORIAL_MASTER.md` - Full tutorial
3. `examples/python/hello_world.py` - First example

### For Developers
Focus on:
1. `python/src/` - Application code
2. `terraform/modules/` - Infrastructure modules
3. `config/` - Configuration files

### For Operations
Key areas:
1. `terraform/environments/` - Environment configs
2. `scripts/deployment/` - Deployment scripts
3. `docs/intermediate/` - Deployment guides

## File Naming Conventions

### Python Files
- `snake_case.py` for all Python files
- `test_*.py` for test files
- `__init__.py` in every package

### Terraform Files
- `main.tf` - Main resources
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `versions.tf` - Provider versions

### Documentation
- `##-description.md` format (e.g., `01-introduction.md`)
- Clear, descriptive names
- Numbered for sequential reading

## Best Practices

### DO ✅
- Keep related files together
- Use descriptive names
- Follow the established structure
- Add README in subdirectories

### DON'T ❌
- Put code in the wrong directory
- Mix configuration with code
- Create unnecessary nesting
- Use inconsistent naming

## Next Steps

Now that you understand the repository structure:
- Explore the `python/src/` directory
- Review a Terraform module
- Try running `examples/python/hello_world.py`

## Quick Reference

| Need to... | Look in... |
|------------|------------|
| Understand a concept | `docs/beginner/` |
| Deploy infrastructure | `terraform/environments/` |
| Write application code | `python/src/` |
| Configure environment | `config/` |
| See examples | `examples/` |
| Run tests | `python/tests/` |
| Automate tasks | `scripts/` |

---

**Tutorial Progress**: 5/100 steps complete 🎯
