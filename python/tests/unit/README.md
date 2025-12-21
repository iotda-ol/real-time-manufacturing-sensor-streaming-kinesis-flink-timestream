# Unit Tests

This directory contains unit tests for individual Python modules.

## Running Unit Tests

```bash
cd python
source venv/bin/activate
pytest tests/unit/ -v
```

## Test Structure

Tests are organized by module:

```
unit/
├── test_data_generator.py      # Tests for DataGenerator
├── test_kinesis_producer.py    # Tests for KinesisProducer
├── test_data_processor.py      # Tests for DataProcessor
├── test_data_transformer.py    # Tests for DataTransformer
├── test_timestream_client.py   # Tests for TimestreamClient
├── test_config_manager.py      # Tests for ConfigManager
└── test_logger.py              # Tests for Logger
```

## Writing Tests

Use pytest conventions:
- Test files: `test_*.py`
- Test functions: `test_*`
- Use fixtures for common setup
- Mock external dependencies

### Example Test

```python
import pytest
from python.src.ingestion import DataGenerator

def test_data_generator_initialization():
    """Test DataGenerator initialization."""
    generator = DataGenerator(num_machines=5)
    assert len(generator.sensors) == 20  # 5 machines * 4 sensors

def test_generate_reading():
    """Test generating a single reading."""
    generator = DataGenerator(num_machines=1)
    sensor = generator.sensors[0]
    reading = generator.generate_reading(sensor)
    
    assert reading.sensor_id is not None
    assert reading.value > 0
    assert reading.timestamp is not None
```

## Test Coverage

Run tests with coverage:

```bash
pytest --cov=python/src tests/unit/ --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Guidelines

- Aim for >80% code coverage
- Test edge cases and error conditions
- Keep tests independent
- Use descriptive test names
