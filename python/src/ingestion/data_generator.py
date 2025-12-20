"""
Data Generator Module

Generates realistic manufacturing sensor data for testing and development.
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SensorReading:
    """Represents a single sensor reading."""
    
    sensor_id: str
    sensor_type: str
    timestamp: str
    value: float
    unit: str
    machine_id: str
    location: str
    quality_status: str = "normal"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class DataGenerator:
    """
    Generates realistic manufacturing sensor data.
    
    Supports multiple sensor types including temperature, pressure,
    vibration, humidity, and power consumption.
    """
    
    SENSOR_TYPES = {
        "temperature": {"min": 15.0, "max": 95.0, "unit": "celsius"},
        "pressure": {"min": 0.5, "max": 10.0, "unit": "bar"},
        "vibration": {"min": 0.0, "max": 5.0, "unit": "mm/s"},
        "humidity": {"min": 20.0, "max": 80.0, "unit": "percent"},
        "power": {"min": 100.0, "max": 5000.0, "unit": "watts"},
    }
    
    def __init__(
        self,
        num_machines: int = 5,
        sensors_per_machine: int = 4,
        location: str = "Factory-A",
    ):
        """
        Initialize the data generator.
        
        Args:
            num_machines: Number of machines to simulate
            sensors_per_machine: Number of sensors per machine
            location: Factory location identifier
        """
        self.num_machines = num_machines
        self.sensors_per_machine = sensors_per_machine
        self.location = location
        self.sensors = self._initialize_sensors()
    
    def _initialize_sensors(self) -> List[Dict]:
        """Initialize sensor configuration."""
        sensors = []
        sensor_types = list(self.SENSOR_TYPES.keys())
        
        for machine_idx in range(self.num_machines):
            machine_id = f"MACHINE-{machine_idx + 1:03d}"
            
            for sensor_idx in range(self.sensors_per_machine):
                sensor_type = sensor_types[sensor_idx % len(sensor_types)]
                sensor_id = f"{machine_id}-{sensor_type.upper()}-{sensor_idx + 1:02d}"
                
                sensors.append({
                    "sensor_id": sensor_id,
                    "sensor_type": sensor_type,
                    "machine_id": machine_id,
                    "config": self.SENSOR_TYPES[sensor_type],
                })
        
        return sensors
    
    def generate_reading(self, sensor: Dict) -> SensorReading:
        """
        Generate a single sensor reading.
        
        Args:
            sensor: Sensor configuration dictionary
            
        Returns:
            SensorReading object
        """
        config = sensor["config"]
        base_value = random.uniform(config["min"], config["max"])
        
        # Add some realistic variation and occasional anomalies
        if random.random() < 0.05:  # 5% chance of anomaly
            value = base_value * random.uniform(1.2, 1.5)
            quality_status = "warning"
        else:
            value = base_value
            quality_status = "normal"
        
        return SensorReading(
            sensor_id=sensor["sensor_id"],
            sensor_type=sensor["sensor_type"],
            timestamp=datetime.utcnow().isoformat() + "Z",
            value=round(value, 2),
            unit=config["unit"],
            machine_id=sensor["machine_id"],
            location=self.location,
            quality_status=quality_status,
        )
    
    def generate_batch(self, batch_size: Optional[int] = None) -> List[SensorReading]:
        """
        Generate a batch of sensor readings.
        
        Args:
            batch_size: Number of readings to generate (default: all sensors)
            
        Returns:
            List of SensorReading objects
        """
        if batch_size is None:
            sensors_to_read = self.sensors
        else:
            sensors_to_read = random.sample(self.sensors, min(batch_size, len(self.sensors)))
        
        return [self.generate_reading(sensor) for sensor in sensors_to_read]
    
    def generate_continuous(
        self,
        interval_seconds: float = 1.0,
        callback: Optional[callable] = None,
    ):
        """
        Generate sensor readings continuously.
        
        Args:
            interval_seconds: Time between batches
            callback: Function to call with each batch of readings
        """
        print(f"Starting continuous data generation (interval: {interval_seconds}s)")
        print(f"Simulating {len(self.sensors)} sensors across {self.num_machines} machines")
        
        try:
            while True:
                readings = self.generate_batch()
                
                if callback:
                    callback(readings)
                else:
                    for reading in readings:
                        print(reading.to_json())
                
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nStopping data generation...")


if __name__ == "__main__":
    # Example usage
    generator = DataGenerator(num_machines=3, sensors_per_machine=3)
    
    # Generate single batch
    batch = generator.generate_batch(5)
    for reading in batch:
        print(reading.to_json())
