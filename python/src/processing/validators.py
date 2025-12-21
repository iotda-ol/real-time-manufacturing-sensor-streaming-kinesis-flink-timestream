"""
Data Validation Module

Validates sensor data for schema compliance and data quality.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class DataValidator:
    """
    Validates sensor data for correctness and quality.
    
    Features:
    - Schema validation
    - Range checking
    - Required field validation
    - Type checking
    """
    
    REQUIRED_FIELDS = [
        "sensor_id",
        "sensor_type",
        "timestamp",
        "value",
        "machine_id",
    ]
    
    SENSOR_TYPE_RANGES = {
        "temperature": {"min": -50.0, "max": 200.0, "unit": "celsius"},
        "pressure": {"min": 0.0, "max": 20.0, "unit": "bar"},
        "vibration": {"min": 0.0, "max": 10.0, "unit": "mm/s"},
        "humidity": {"min": 0.0, "max": 100.0, "unit": "percent"},
        "power": {"min": 0.0, "max": 10000.0, "unit": "watts"},
    }
    
    def __init__(self):
        """Initialize validator."""
        self.validation_stats = {
            "total_validated": 0,
            "valid": 0,
            "invalid": 0,
        }
    
    def validate_reading(
        self,
        reading: Dict,
        strict: bool = True,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a single sensor reading.
        
        Args:
            reading: Sensor reading dictionary
            strict: If True, fail on any validation error
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        self.validation_stats["total_validated"] += 1
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in reading:
                error = f"Missing required field: {field}"
                self.validation_stats["invalid"] += 1
                return False, error
        
        # Validate sensor type
        sensor_type = reading.get("sensor_type")
        if sensor_type not in self.SENSOR_TYPE_RANGES:
            error = f"Unknown sensor type: {sensor_type}"
            if strict:
                self.validation_stats["invalid"] += 1
                return False, error
        
        # Validate value range
        value = reading.get("value")
        if not isinstance(value, (int, float)):
            error = f"Invalid value type: {type(value)}"
            self.validation_stats["invalid"] += 1
            return False, error
        
        if sensor_type in self.SENSOR_TYPE_RANGES:
            range_config = self.SENSOR_TYPE_RANGES[sensor_type]
            if not (range_config["min"] <= value <= range_config["max"]):
                error = (
                    f"Value {value} out of range "
                    f"[{range_config['min']}, {range_config['max']}]"
                )
                if strict:
                    self.validation_stats["invalid"] += 1
                    return False, error
        
        # Validate timestamp format
        timestamp = reading.get("timestamp")
        if not self._validate_timestamp(timestamp):
            error = f"Invalid timestamp format: {timestamp}"
            self.validation_stats["invalid"] += 1
            return False, error
        
        self.validation_stats["valid"] += 1
        return True, None
    
    def validate_batch(
        self,
        readings: List[Dict],
        strict: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate a batch of readings.
        
        Args:
            readings: List of sensor readings
            strict: If True, stop on first error
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid_readings": [],
            "invalid_readings": [],
            "errors": [],
        }
        
        for reading in readings:
            is_valid, error = self.validate_reading(reading, strict)
            
            if is_valid:
                results["valid_readings"].append(reading)
            else:
                results["invalid_readings"].append(reading)
                results["errors"].append({
                    "reading": reading,
                    "error": error,
                })
                
                if strict:
                    break
        
        return results
    
    def _validate_timestamp(self, timestamp: str) -> bool:
        """
        Validate timestamp format (ISO 8601).
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            True if valid, False otherwise
        """
        if not timestamp or not isinstance(timestamp, str):
            return False
        
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get validation statistics."""
        return self.validation_stats.copy()
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.validation_stats = {
            "total_validated": 0,
            "valid": 0,
            "invalid": 0,
        }


if __name__ == "__main__":
    # Example usage
    validator = DataValidator()
    
    # Valid reading
    valid_reading = {
        "sensor_id": "SENSOR-001",
        "sensor_type": "temperature",
        "timestamp": "2024-01-01T00:00:00Z",
        "value": 25.5,
        "machine_id": "MACHINE-001",
    }
    
    is_valid, error = validator.validate_reading(valid_reading)
    print(f"Valid: {is_valid}, Error: {error}")
    
    # Invalid reading (out of range)
    invalid_reading = valid_reading.copy()
    invalid_reading["value"] = 500.0  # Too high
    
    is_valid, error = validator.validate_reading(invalid_reading)
    print(f"Valid: {is_valid}, Error: {error}")
    
    # Statistics
    print(f"Stats: {validator.get_stats()}")
