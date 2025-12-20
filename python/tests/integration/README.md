# Integration Tests

This directory contains integration tests that test components working together with real AWS services.

## Running Integration Tests

**Warning**: These tests interact with real AWS services and may incur costs.

```bash
cd python
source venv/bin/activate

# Set AWS credentials
export AWS_REGION=us-east-1

# Run integration tests
pytest tests/integration/ -v
```

## Test Structure

```
integration/
├── test_kinesis_integration.py       # Kinesis end-to-end tests
├── test_timestream_integration.py    # Timestream read/write tests
└── test_pipeline_integration.py      # Complete pipeline tests
```

## Prerequisites

Before running integration tests:
1. Deploy test infrastructure (dev environment)
2. Configure AWS credentials
3. Set environment variables for resource names

### Environment Variables

```bash
export KINESIS_STREAM_NAME=manufacturing-sensor-stream-dev
export TIMESTREAM_DATABASE=manufacturing_db_dev
export TIMESTREAM_TABLE=sensor_data
```

## Writing Integration Tests

Use real AWS services but clean up after tests:

```python
import pytest
import boto3
from python.src.ingestion import KinesisProducer

@pytest.fixture
def kinesis_producer():
    """Create KinesisProducer for testing."""
    return KinesisProducer(
        stream_name=os.getenv("KINESIS_STREAM_NAME"),
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

def test_send_to_kinesis(kinesis_producer):
    """Test sending data to real Kinesis stream."""
    test_data = {
        "sensor_id": "TEST-001",
        "value": 42.0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    response = kinesis_producer.put_record(test_data)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
```

## Best Practices

- Use fixtures for setup/teardown
- Clean up resources after tests
- Use test-specific resource names
- Skip tests if infrastructure not available
- Tag slow tests: `@pytest.mark.slow`

## Skipping Tests

If infrastructure not deployed:

```python
@pytest.mark.skipif(
    not os.getenv("KINESIS_STREAM_NAME"),
    reason="Kinesis stream not configured"
)
def test_kinesis_integration():
    pass
```
