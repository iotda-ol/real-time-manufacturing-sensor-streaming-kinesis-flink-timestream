"""
Timestream Client Module

Provides a wrapper for Amazon Timestream operations.
"""

import logging
from typing import List, Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError


class TimestreamClient:
    """
    Amazon Timestream client wrapper with simplified operations.
    
    Features:
    - Database and table management
    - Record insertion with batch support
    - Query execution
    - Error handling and retries
    """
    
    def __init__(
        self,
        database_name: str,
        table_name: str,
        region_name: str = "us-east-1",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Timestream client.
        
        Args:
            database_name: Timestream database name
            table_name: Timestream table name
            region_name: AWS region
            logger: Optional logger instance
        """
        self.database_name = database_name
        self.table_name = table_name
        self.region_name = region_name
        self.logger = logger or logging.getLogger(__name__)
        
        self.write_client = boto3.client(
            "timestream-write",
            region_name=region_name
        )
        self.query_client = boto3.client(
            "timestream-query",
            region_name=region_name
        )
    
    def create_database(self) -> bool:
        """
        Create Timestream database if it doesn't exist.
        
        Returns:
            True if created or already exists, False on error
        """
        try:
            self.write_client.create_database(DatabaseName=self.database_name)
            self.logger.info(f"Created database: {self.database_name}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                self.logger.info(f"Database already exists: {self.database_name}")
                return True
            else:
                self.logger.error(f"Failed to create database: {e}")
                return False
    
    def create_table(
        self,
        memory_retention_hours: int = 24,
        magnetic_retention_days: int = 365,
    ) -> bool:
        """
        Create Timestream table if it doesn't exist.
        
        Args:
            memory_retention_hours: Retention in memory store (hours)
            magnetic_retention_days: Retention in magnetic store (days)
            
        Returns:
            True if created or already exists, False on error
        """
        try:
            self.write_client.create_table(
                DatabaseName=self.database_name,
                TableName=self.table_name,
                RetentionProperties={
                    "MemoryStoreRetentionPeriodInHours": memory_retention_hours,
                    "MagneticStoreRetentionPeriodInDays": magnetic_retention_days,
                }
            )
            self.logger.info(f"Created table: {self.table_name}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                self.logger.info(f"Table already exists: {self.table_name}")
                return True
            else:
                self.logger.error(f"Failed to create table: {e}")
                return False
    
    def write_records(
        self,
        records: List[Dict[str, Any]],
        common_attributes: Optional[Dict] = None,
    ) -> Dict[str, int]:
        """
        Write records to Timestream table.
        
        Args:
            records: List of Timestream-formatted records
            common_attributes: Optional common attributes for all records
            
        Returns:
            Dictionary with success and rejection counts
        """
        if not records:
            return {"success": 0, "rejected": 0}
        
        # Timestream allows max 100 records per request
        batch_size = 100
        results = {"success": 0, "rejected": 0}
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            try:
                write_params = {
                    "DatabaseName": self.database_name,
                    "TableName": self.table_name,
                    "Records": batch,
                }
                
                if common_attributes:
                    write_params["CommonAttributes"] = common_attributes
                
                response = self.write_client.write_records(**write_params)
                
                results["success"] += len(batch)
                
                if "RejectedRecords" in response and response["RejectedRecords"]:
                    rejected_count = len(response["RejectedRecords"])
                    results["rejected"] += rejected_count
                    results["success"] -= rejected_count
                    
                    for rejected in response["RejectedRecords"]:
                        self.logger.warning(
                            f"Rejected record: {rejected.get('Reason', 'Unknown')}"
                        )
            
            except ClientError as e:
                self.logger.error(f"Failed to write records batch: {e}")
                results["rejected"] += len(batch)
        
        self.logger.info(
            f"Wrote {results['success']} records, {results['rejected']} rejected"
        )
        
        return results
    
    def query(self, query_string: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        """
        Execute a query against Timestream.
        
        Args:
            query_string: SQL query string
            max_rows: Maximum rows to return
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            response = self.query_client.query(QueryString=query_string)
            
            rows = []
            column_info = response.get("ColumnInfo", [])
            
            for row in response.get("Rows", []):
                row_dict = {}
                for i, data in enumerate(row.get("Data", [])):
                    if i < len(column_info):
                        column_name = column_info[i]["Name"]
                        
                        # Extract value from ScalarValue or other types
                        if "ScalarValue" in data:
                            row_dict[column_name] = data["ScalarValue"]
                        elif "NullValue" in data:
                            row_dict[column_name] = None
                        else:
                            row_dict[column_name] = str(data)
                
                rows.append(row_dict)
                
                if len(rows) >= max_rows:
                    break
            
            self.logger.info(f"Query returned {len(rows)} rows")
            return rows
        
        except ClientError as e:
            self.logger.error(f"Query failed: {e}")
            return []
    
    def query_latest_by_sensor(
        self,
        sensor_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Query latest readings for a specific sensor.
        
        Args:
            sensor_id: Sensor identifier
            limit: Maximum number of readings
            
        Returns:
            List of readings
        """
        query = f"""
        SELECT *
        FROM "{self.database_name}"."{self.table_name}"
        WHERE sensor_id = '{sensor_id}'
        ORDER BY time DESC
        LIMIT {limit}
        """
        
        return self.query(query)
    
    def query_time_range(
        self,
        start_time: str,
        end_time: str,
        sensor_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query readings within a time range.
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            sensor_type: Optional sensor type filter
            
        Returns:
            List of readings
        """
        query = f"""
        SELECT *
        FROM "{self.database_name}"."{self.table_name}"
        WHERE time BETWEEN from_iso8601_timestamp('{start_time}')
                       AND from_iso8601_timestamp('{end_time}')
        """
        
        if sensor_type:
            query += f" AND sensor_type = '{sensor_type}'"
        
        query += " ORDER BY time DESC"
        
        return self.query(query)
    
    def describe_table(self) -> Optional[Dict[str, Any]]:
        """
        Get table description and metadata.
        
        Returns:
            Table description dictionary or None
        """
        try:
            response = self.write_client.describe_table(
                DatabaseName=self.database_name,
                TableName=self.table_name,
            )
            return response.get("Table")
        except ClientError as e:
            self.logger.error(f"Failed to describe table: {e}")
            return None
    
    def delete_table(self) -> bool:
        """
        Delete the Timestream table.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.write_client.delete_table(
                DatabaseName=self.database_name,
                TableName=self.table_name,
            )
            self.logger.info(f"Deleted table: {self.table_name}")
            return True
        except ClientError as e:
            self.logger.error(f"Failed to delete table: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    client = TimestreamClient(
        database_name="manufacturing_db",
        table_name="sensor_data",
    )
    
    # Query example
    results = client.query_latest_by_sensor("SENSOR-001", limit=5)
    print(f"Retrieved {len(results)} records")
