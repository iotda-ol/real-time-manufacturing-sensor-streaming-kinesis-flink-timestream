#!/usr/bin/env python3
"""
Hello World Example

A simple example demonstrating the basic usage of the data generator
and Kinesis producer.

This is your first step in learning the system (Tutorial Step 25).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from python.src.ingestion import DataGenerator


def main():
    """Run hello world example."""
    print("=" * 60)
    print("Hello World - Manufacturing Sensor Streaming")
    print("=" * 60)
    print()
    
    # Create a simple data generator
    generator = DataGenerator(
        num_machines=2,
        sensors_per_machine=2,
        location="Factory-HelloWorld"
    )
    
    print(f"Initialized generator with {len(generator.sensors)} sensors")
    print()
    
    # Generate some sample data
    print("Generating 5 sensor readings...")
    print()
    
    readings = generator.generate_batch(5)
    
    for i, reading in enumerate(readings, 1):
        print(f"Reading {i}:")
        print(f"  Sensor ID: {reading.sensor_id}")
        print(f"  Type: {reading.sensor_type}")
        print(f"  Value: {reading.value} {reading.unit}")
        print(f"  Machine: {reading.machine_id}")
        print(f"  Timestamp: {reading.timestamp}")
        print()
    
    print("=" * 60)
    print("Hello World Complete!")
    print("Next: Try running the E2E example to send data to Kinesis")
    print("=" * 60)


if __name__ == "__main__":
    main()
