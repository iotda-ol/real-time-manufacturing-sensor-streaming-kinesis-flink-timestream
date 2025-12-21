# End-to-End Tests

This directory contains end-to-end tests that validate the complete data pipeline.

## Overview

E2E tests verify the entire system from data generation through visualization:
1. Generate sensor data
2. Send to Kinesis
3. Process with Flink
4. Store in Timestream
5. Query and verify results

## Running E2E Tests

**Prerequisites**:
- Complete infrastructure deployed
- All services running
- Sufficient AWS permissions

```bash
cd python
source venv/bin/activate

# Run e2e tests
pytest tests/e2e/ -v --slow
```

## Test Structure

```
e2e/
├── test_complete_pipeline.py      # Full pipeline test
├── test_data_accuracy.py          # Data accuracy validation
└── test_performance.py            # Performance benchmarks
```

## Example Test Flow

```python
def test_complete_data_pipeline():
    """Test complete data flow through pipeline."""
    
    # 1. Generate test data
    generator = DataGenerator(num_machines=1)
    readings = generator.generate_batch(10)
    
    # 2. Send to Kinesis
    producer = KinesisProducer(stream_name="test-stream")
    producer.put_sensor_readings(readings)
    
    # 3. Wait for processing (Flink)
    time.sleep(30)
    
    # 4. Verify in Timestream
    client = TimestreamClient(database="test_db", table="test_table")
    results = client.query_latest_by_sensor(readings[0].sensor_id)
    
    # 5. Validate
    assert len(results) > 0
    assert results[0]["sensor_id"] == readings[0].sensor_id
```

## Configuration

Set test configuration in environment:

```bash
export E2E_ENVIRONMENT=dev
export E2E_WAIT_TIME=60  # Seconds to wait for processing
export E2E_CLEANUP=true  # Clean up test data after run
```

## Best Practices

- Use dedicated test resources
- Clean up after tests
- Allow sufficient processing time
- Validate data accuracy
- Test error scenarios
- Monitor costs

## Test Markers

Use pytest markers:
- `@pytest.mark.e2e` - End-to-end test
- `@pytest.mark.slow` - Long-running test
- `@pytest.mark.expensive` - Tests that incur AWS costs

Run specific markers:
```bash
pytest -m "e2e and not expensive"
```
