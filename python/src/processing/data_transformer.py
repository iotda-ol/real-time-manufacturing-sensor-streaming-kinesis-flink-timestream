"""
Data Transformer Module

Transforms sensor data between different formats and structures.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class DataTransformer:
    """
    Transforms sensor data between formats.
    
    Supports transformations for:
    - Timestream format
    - Grafana format
    - CSV export
    - Aggregated views
    """
    
    @staticmethod
    def to_timestream_record(reading: Dict) -> Dict[str, Any]:
        """
        Transform reading to Timestream record format.
        
        Args:
            reading: Sensor reading dictionary
            
        Returns:
            Timestream-formatted record
        """
        dimensions = [
            {"Name": "sensor_id", "Value": str(reading.get("sensor_id", ""))},
            {"Name": "machine_id", "Value": str(reading.get("machine_id", ""))},
            {"Name": "sensor_type", "Value": str(reading.get("sensor_type", ""))},
            {"Name": "location", "Value": str(reading.get("location", ""))},
        ]
        
        # Add quality status if present
        if "quality_status" in reading:
            dimensions.append({
                "Name": "quality_status",
                "Value": str(reading["quality_status"])
            })
        
        record = {
            "Dimensions": dimensions,
            "MeasureName": reading.get("sensor_type", "measurement"),
            "MeasureValue": str(reading.get("value", 0)),
            "MeasureValueType": "DOUBLE",
            "Time": DataTransformer._convert_timestamp(reading.get("timestamp")),
            "TimeUnit": "MILLISECONDS",
        }
        
        return record
    
    @staticmethod
    def to_timestream_records_batch(readings: List[Dict]) -> List[Dict[str, Any]]:
        """
        Transform multiple readings to Timestream format.
        
        Args:
            readings: List of sensor readings
            
        Returns:
            List of Timestream-formatted records
        """
        return [DataTransformer.to_timestream_record(r) for r in readings]
    
    @staticmethod
    def to_csv_row(reading: Dict) -> str:
        """
        Transform reading to CSV row.
        
        Args:
            reading: Sensor reading dictionary
            
        Returns:
            CSV-formatted string
        """
        fields = [
            reading.get("timestamp", ""),
            reading.get("sensor_id", ""),
            reading.get("machine_id", ""),
            reading.get("sensor_type", ""),
            str(reading.get("value", "")),
            reading.get("unit", ""),
            reading.get("location", ""),
            reading.get("quality_status", ""),
        ]
        
        return ",".join(f'"{field}"' for field in fields)
    
    @staticmethod
    def to_csv(readings: List[Dict], include_header: bool = True) -> str:
        """
        Transform readings to CSV format.
        
        Args:
            readings: List of sensor readings
            include_header: Include CSV header row
            
        Returns:
            CSV-formatted string
        """
        lines = []
        
        if include_header:
            header = "timestamp,sensor_id,machine_id,sensor_type,value,unit,location,quality_status"
            lines.append(header)
        
        for reading in readings:
            lines.append(DataTransformer.to_csv_row(reading))
        
        return "\n".join(lines)
    
    @staticmethod
    def from_json(json_str: str) -> Dict:
        """
        Parse JSON string to dictionary.
        
        Args:
            json_str: JSON string
            
        Returns:
            Parsed dictionary
        """
        return json.loads(json_str)
    
    @staticmethod
    def to_json(data: Any, pretty: bool = False) -> str:
        """
        Convert data to JSON string.
        
        Args:
            data: Data to convert
            pretty: Use pretty formatting
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=2, sort_keys=True)
        return json.dumps(data)
    
    @staticmethod
    def aggregate_time_window(
        readings: List[Dict],
        window_seconds: int = 60,
        aggregation: str = "mean",
    ) -> List[Dict]:
        """
        Aggregate readings into time windows.
        
        Args:
            readings: List of sensor readings
            window_seconds: Size of time window in seconds
            aggregation: Aggregation method ('mean', 'sum', 'min', 'max')
            
        Returns:
            List of aggregated readings
        """
        # Group by time window and sensor
        windows = {}
        
        for reading in readings:
            timestamp = reading.get("timestamp", "")
            sensor_id = reading.get("sensor_id", "")
            
            # Calculate window key
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            window_start = int(dt.timestamp() / window_seconds) * window_seconds
            
            key = (window_start, sensor_id)
            
            if key not in windows:
                windows[key] = {
                    "values": [],
                    "base_reading": reading.copy(),
                }
            
            windows[key]["values"].append(reading.get("value", 0))
        
        # Aggregate each window
        aggregated = []
        for (window_start, sensor_id), data in windows.items():
            values = data["values"]
            base = data["base_reading"]
            
            if aggregation == "mean":
                agg_value = sum(values) / len(values)
            elif aggregation == "sum":
                agg_value = sum(values)
            elif aggregation == "min":
                agg_value = min(values)
            elif aggregation == "max":
                agg_value = max(values)
            else:
                agg_value = sum(values) / len(values)
            
            aggregated_reading = base.copy()
            aggregated_reading["value"] = round(agg_value, 2)
            aggregated_reading["timestamp"] = datetime.fromtimestamp(window_start).isoformat() + "Z"
            aggregated_reading["aggregation"] = aggregation
            aggregated_reading["window_seconds"] = window_seconds
            aggregated_reading["sample_count"] = len(values)
            
            aggregated.append(aggregated_reading)
        
        return aggregated
    
    @staticmethod
    def _convert_timestamp(timestamp: Optional[str]) -> str:
        """
        Convert ISO timestamp to milliseconds since epoch.
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Milliseconds since epoch as string
        """
        if not timestamp:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        milliseconds = int(dt.timestamp() * 1000)
        return str(milliseconds)
    
    @staticmethod
    def flatten_nested(data: Dict, prefix: str = "", separator: str = "_") -> Dict:
        """
        Flatten nested dictionary.
        
        Args:
            data: Nested dictionary
            prefix: Prefix for keys
            separator: Separator between nested keys
            
        Returns:
            Flattened dictionary
        """
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(
                    DataTransformer.flatten_nested(value, new_key, separator)
                )
            else:
                flattened[new_key] = value
        
        return flattened
