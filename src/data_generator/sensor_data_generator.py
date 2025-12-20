#!/usr/bin/env python3
"""
Manufacturing Sensor Data Generator
Generates realistic sensor data and sends it to Amazon Kinesis Data Streams
"""

import json
import time
import random
import argparse
from datetime import datetime
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError

class SensorDataGenerator:
    """Generates realistic manufacturing sensor data"""
    
    MACHINE_IDS = ["M001", "M002", "M003", "M004", "M005"]
    SENSOR_TYPES = ["temperature", "pressure", "vibration", "power_consumption", "cycle_time"]
    
    # Normal operating ranges for each sensor type
    SENSOR_RANGES = {
        "temperature": (60.0, 80.0),
        "pressure": (90.0, 110.0),
        "vibration": (0.1, 0.5),
        "power_consumption": (500.0, 1500.0),
        "cycle_time": (30.0, 60.0)
    }
    
    # Anomaly thresholds
    ANOMALY_THRESHOLDS = {
        "temperature": 95.0,
        "pressure": 120.0,
        "vibration": 0.8,
        "power_consumption": 2000.0,
        "cycle_time": 90.0
    }
    
    def __init__(self, stream_name: str, region: str = "us-east-1"):
        """Initialize the sensor data generator"""
        self.stream_name = stream_name
        self.kinesis_client = boto3.client('kinesis', region_name=region)
        self.sequence_number = 0
        
    def generate_sensor_reading(
        self, 
        machine_id: str, 
        sensor_type: str,
        inject_anomaly: bool = False
    ) -> Dict:
        """Generate a single sensor reading"""
        
        min_val, max_val = self.SENSOR_RANGES[sensor_type]
        
        if inject_anomaly:
            # Generate anomalous value above threshold
            value = random.uniform(
                self.ANOMALY_THRESHOLDS[sensor_type],
                self.ANOMALY_THRESHOLDS[sensor_type] * 1.2
            )
            status = "ANOMALY"
        else:
            # Generate normal value with slight random variation
            value = random.uniform(min_val, max_val)
            status = "NORMAL"
        
        self.sequence_number += 1
        
        return {
            "machine_id": machine_id,
            "sensor_type": sensor_type,
            "value": round(value, 2),
            "unit": self._get_unit(sensor_type),
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "sequence_number": self.sequence_number,
            "metadata": {
                "location": f"Factory-Floor-{machine_id[1]}",
                "production_line": f"Line-{random.randint(1, 3)}"
            }
        }
    
    def _get_unit(self, sensor_type: str) -> str:
        """Get measurement unit for sensor type"""
        units = {
            "temperature": "celsius",
            "pressure": "psi",
            "vibration": "mm/s",
            "power_consumption": "watts",
            "cycle_time": "seconds"
        }
        return units.get(sensor_type, "unknown")
    
    def send_to_kinesis(self, data: Dict) -> bool:
        """Send data to Kinesis Data Stream"""
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(data),
                PartitionKey=data['machine_id']
            )
            
            print(f"✓ Sent: {data['machine_id']} | {data['sensor_type']} | "
                  f"{data['value']} {data['unit']} | {data['status']}")
            
            return True
            
        except ClientError as e:
            print(f"✗ Error sending to Kinesis: {e}")
            return False
    
    def send_batch_to_kinesis(self, records: List[Dict]) -> Dict:
        """Send batch of records to Kinesis"""
        try:
            kinesis_records = [
                {
                    'Data': json.dumps(record),
                    'PartitionKey': record['machine_id']
                }
                for record in records
            ]
            
            response = self.kinesis_client.put_records(
                StreamName=self.stream_name,
                Records=kinesis_records
            )
            
            failed_count = response['FailedRecordCount']
            success_count = len(records) - failed_count
            
            print(f"✓ Batch sent: {success_count} succeeded, {failed_count} failed")
            
            return response
            
        except ClientError as e:
            print(f"✗ Error sending batch to Kinesis: {e}")
            return {'FailedRecordCount': len(records)}
    
    def generate_continuous_data(
        self, 
        interval_seconds: float = 1.0,
        anomaly_probability: float = 0.05,
        batch_size: int = 10
    ):
        """Continuously generate and send sensor data"""
        print(f"Starting sensor data generation...")
        print(f"Stream: {self.stream_name}")
        print(f"Interval: {interval_seconds}s")
        print(f"Anomaly probability: {anomaly_probability * 100}%")
        print(f"Batch size: {batch_size}")
        print("-" * 70)
        
        batch = []
        
        try:
            while True:
                for machine_id in self.MACHINE_IDS:
                    for sensor_type in self.SENSOR_TYPES:
                        # Randomly inject anomalies
                        inject_anomaly = random.random() < anomaly_probability
                        
                        reading = self.generate_sensor_reading(
                            machine_id, 
                            sensor_type, 
                            inject_anomaly
                        )
                        
                        batch.append(reading)
                        
                        # Send batch when full
                        if len(batch) >= batch_size:
                            self.send_batch_to_kinesis(batch)
                            batch = []
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\nStopping data generation...")
            if batch:
                self.send_batch_to_kinesis(batch)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate manufacturing sensor data for Kinesis'
    )
    parser.add_argument(
        '--stream-name',
        type=str,
        required=True,
        help='Name of the Kinesis Data Stream'
    )
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Interval between data generation cycles in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--anomaly-rate',
        type=float,
        default=0.05,
        help='Probability of generating anomalous data (default: 0.05)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of records to batch before sending (default: 10)'
    )
    
    args = parser.parse_args()
    
    generator = SensorDataGenerator(
        stream_name=args.stream_name,
        region=args.region
    )
    
    generator.generate_continuous_data(
        interval_seconds=args.interval,
        anomaly_probability=args.anomaly_rate,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
