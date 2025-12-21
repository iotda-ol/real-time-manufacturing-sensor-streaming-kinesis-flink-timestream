"""
Kinesis Producer Module

Provides a robust producer for sending data to Amazon Kinesis Data Streams.
"""

import json
import logging
import time
from typing import List, Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError


class KinesisProducer:
    """
    Kinesis Data Streams producer with error handling and retry logic.
    
    Features:
    - Automatic retries with exponential backoff
    - Batch processing support
    - Partition key generation
    - Error handling and logging
    """
    
    def __init__(
        self,
        stream_name: str,
        region_name: str = "us-east-1",
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Kinesis producer.
        
        Args:
            stream_name: Name of the Kinesis stream
            region_name: AWS region
            max_retries: Maximum number of retry attempts
            logger: Optional logger instance
        """
        self.stream_name = stream_name
        self.region_name = region_name
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)
        
        self.client = boto3.client("kinesis", region_name=region_name)
        self._verify_stream()
    
    def _verify_stream(self):
        """Verify that the Kinesis stream exists and is active."""
        try:
            response = self.client.describe_stream(StreamName=self.stream_name)
            status = response["StreamDescription"]["StreamStatus"]
            
            if status != "ACTIVE":
                self.logger.warning(f"Stream {self.stream_name} status: {status}")
            else:
                self.logger.info(f"Connected to Kinesis stream: {self.stream_name}")
        except ClientError as e:
            self.logger.error(f"Failed to verify stream: {e}")
            raise
    
    def _generate_partition_key(self, data: Dict) -> str:
        """
        Generate partition key from data.
        
        Uses machine_id or sensor_id for even distribution across shards.
        
        Args:
            data: Data dictionary
            
        Returns:
            Partition key string
        """
        if "machine_id" in data:
            return data["machine_id"]
        elif "sensor_id" in data:
            return data["sensor_id"]
        else:
            return str(hash(json.dumps(data, sort_keys=True)))
    
    def put_record(
        self,
        data: Dict,
        partition_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Put a single record to Kinesis stream.
        
        Args:
            data: Data dictionary to send
            partition_key: Optional partition key (auto-generated if not provided)
            
        Returns:
            Kinesis response dictionary
        """
        if partition_key is None:
            partition_key = self._generate_partition_key(data)
        
        data_bytes = json.dumps(data).encode("utf-8")
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.put_record(
                    StreamName=self.stream_name,
                    Data=data_bytes,
                    PartitionKey=partition_key,
                )
                
                self.logger.debug(
                    f"Successfully put record to shard {response['ShardId']}"
                )
                return response
            
            except ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to put record after {self.max_retries} attempts")
                    raise
    
    def put_records_batch(
        self,
        records: List[Dict],
        batch_size: int = 500,
    ) -> Dict[str, int]:
        """
        Put multiple records to Kinesis in batches.
        
        Args:
            records: List of data dictionaries
            batch_size: Maximum records per batch (max 500)
            
        Returns:
            Dictionary with success and failure counts
        """
        batch_size = min(batch_size, 500)  # Kinesis limit
        results = {"success": 0, "failed": 0}
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            kinesis_records = [
                {
                    "Data": json.dumps(record).encode("utf-8"),
                    "PartitionKey": self._generate_partition_key(record),
                }
                for record in batch
            ]
            
            try:
                response = self.client.put_records(
                    StreamName=self.stream_name,
                    Records=kinesis_records,
                )
                
                results["success"] += len(batch) - response["FailedRecordCount"]
                results["failed"] += response["FailedRecordCount"]
                
                if response["FailedRecordCount"] > 0:
                    self.logger.warning(
                        f"Batch had {response['FailedRecordCount']} failed records"
                    )
                
            except ClientError as e:
                self.logger.error(f"Failed to put batch: {e}")
                results["failed"] += len(batch)
        
        self.logger.info(
            f"Batch processing complete: {results['success']} succeeded, "
            f"{results['failed']} failed"
        )
        
        return results
    
    def put_sensor_readings(self, readings: List[Any]) -> Dict[str, int]:
        """
        Put sensor readings to Kinesis.
        
        Args:
            readings: List of SensorReading objects or dictionaries
            
        Returns:
            Dictionary with success and failure counts
        """
        records = []
        for reading in readings:
            if hasattr(reading, "to_dict"):
                records.append(reading.to_dict())
            else:
                records.append(reading)
        
        return self.put_records_batch(records)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize producer
    producer = KinesisProducer(
        stream_name="manufacturing-sensor-stream",
        region_name="us-east-1",
    )
    
    # Send test data
    test_data = {
        "sensor_id": "TEST-001",
        "machine_id": "MACHINE-001",
        "timestamp": "2024-01-01T00:00:00Z",
        "value": 42.5,
        "sensor_type": "temperature",
    }
    
    response = producer.put_record(test_data)
    print(f"Record sent: {response}")
