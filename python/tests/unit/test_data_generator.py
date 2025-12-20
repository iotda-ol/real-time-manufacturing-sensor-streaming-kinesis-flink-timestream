"""
Unit tests for DataGenerator module.
"""

import pytest
from datetime import datetime
from python.src.ingestion.data_generator import DataGenerator, SensorReading


class TestSensorReading:
    """Tests for SensorReading dataclass."""
    
    def test_sensor_reading_creation(self):
        """Test creating a SensorReading instance."""
        reading = SensorReading(
            sensor_id="TEST-001",
            sensor_type="temperature",
            timestamp="2024-01-01T00:00:00Z",
            value=25.5,
            unit="celsius",
            machine_id="MACHINE-001",
            location="Factory-A",
        )
        
        assert reading.sensor_id == "TEST-001"
        assert reading.sensor_type == "temperature"
        assert reading.value == 25.5
        assert reading.quality_status == "normal"
    
    def test_to_dict(self):
        """Test converting SensorReading to dictionary."""
        reading = SensorReading(
            sensor_id="TEST-001",
            sensor_type="temperature",
            timestamp="2024-01-01T00:00:00Z",
            value=25.5,
            unit="celsius",
            machine_id="MACHINE-001",
            location="Factory-A",
        )
        
        data = reading.to_dict()
        
        assert isinstance(data, dict)
        assert data["sensor_id"] == "TEST-001"
        assert data["value"] == 25.5
    
    def test_to_json(self):
        """Test converting SensorReading to JSON string."""
        reading = SensorReading(
            sensor_id="TEST-001",
            sensor_type="temperature",
            timestamp="2024-01-01T00:00:00Z",
            value=25.5,
            unit="celsius",
            machine_id="MACHINE-001",
            location="Factory-A",
        )
        
        json_str = reading.to_json()
        
        assert isinstance(json_str, str)
        assert "TEST-001" in json_str
        assert "25.5" in json_str


class TestDataGenerator:
    """Tests for DataGenerator class."""
    
    def test_initialization(self):
        """Test DataGenerator initialization."""
        generator = DataGenerator(
            num_machines=5,
            sensors_per_machine=4,
            location="Factory-Test"
        )
        
        assert generator.num_machines == 5
        assert generator.sensors_per_machine == 4
        assert generator.location == "Factory-Test"
        assert len(generator.sensors) == 20  # 5 * 4
    
    def test_sensor_initialization(self):
        """Test that sensors are initialized correctly."""
        generator = DataGenerator(num_machines=2, sensors_per_machine=3)
        
        assert len(generator.sensors) == 6
        
        # Check sensor structure
        sensor = generator.sensors[0]
        assert "sensor_id" in sensor
        assert "sensor_type" in sensor
        assert "machine_id" in sensor
        assert "config" in sensor
    
    def test_generate_reading(self):
        """Test generating a single sensor reading."""
        generator = DataGenerator(num_machines=1, sensors_per_machine=1)
        sensor = generator.sensors[0]
        
        reading = generator.generate_reading(sensor)
        
        assert isinstance(reading, SensorReading)
        assert reading.sensor_id == sensor["sensor_id"]
        assert reading.sensor_type == sensor["sensor_type"]
        assert reading.machine_id == sensor["machine_id"]
        assert reading.value >= 0
    
    def test_generate_reading_value_range(self):
        """Test that generated values are within expected range."""
        generator = DataGenerator(num_machines=1, sensors_per_machine=1)
        
        # Generate many readings to test range
        for _ in range(100):
            for sensor in generator.sensors:
                reading = generator.generate_reading(sensor)
                config = sensor["config"]
                
                # Allow for anomalies (up to 1.5x max)
                assert reading.value >= config["min"]
                assert reading.value <= config["max"] * 1.5
    
    def test_generate_batch(self):
        """Test generating a batch of readings."""
        generator = DataGenerator(num_machines=2, sensors_per_machine=2)
        
        batch = generator.generate_batch()
        
        assert len(batch) == 4  # All sensors
        assert all(isinstance(r, SensorReading) for r in batch)
    
    def test_generate_batch_with_size(self):
        """Test generating a batch with specified size."""
        generator = DataGenerator(num_machines=5, sensors_per_machine=4)
        
        batch = generator.generate_batch(batch_size=10)
        
        assert len(batch) == 10
    
    def test_generate_batch_size_limit(self):
        """Test that batch size doesn't exceed available sensors."""
        generator = DataGenerator(num_machines=1, sensors_per_machine=1)
        
        batch = generator.generate_batch(batch_size=100)
        
        assert len(batch) == 1  # Only 1 sensor available
    
    def test_reading_has_timestamp(self):
        """Test that generated readings have valid timestamps."""
        generator = DataGenerator(num_machines=1, sensors_per_machine=1)
        sensor = generator.sensors[0]
        
        reading = generator.generate_reading(sensor)
        
        assert reading.timestamp is not None
        # Verify ISO format with Z suffix
        assert reading.timestamp.endswith("Z")
        
        # Parse timestamp to verify format
        timestamp = reading.timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(timestamp)
        assert isinstance(dt, datetime)
    
    def test_sensor_types_coverage(self):
        """Test that all sensor types are covered."""
        generator = DataGenerator(num_machines=2, sensors_per_machine=5)
        
        sensor_types = set(s["sensor_type"] for s in generator.sensors)
        
        # Should have multiple types
        assert len(sensor_types) > 1
        
        # All types should be valid
        for sensor_type in sensor_types:
            assert sensor_type in DataGenerator.SENSOR_TYPES
    
    def test_anomaly_generation(self):
        """Test that some readings are marked as anomalies."""
        generator = DataGenerator(num_machines=5, sensors_per_machine=4)
        
        # Generate many readings to ensure some anomalies
        anomaly_count = 0
        for _ in range(1000):
            batch = generator.generate_batch()
            anomaly_count += sum(
                1 for r in batch if r.quality_status == "warning"
            )
        
        # Should have some anomalies (roughly 5% = 50 out of 1000)
        assert anomaly_count > 0
        assert anomaly_count < 200  # Not too many


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
