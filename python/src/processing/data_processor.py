"""
Data Processor Module

Core data processing logic for sensor readings.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics


class DataProcessor:
    """
    Processes sensor data with aggregations, filtering, and enrichment.
    """
    
    def __init__(self):
        """Initialize data processor."""
        self.processing_stats = {"total_processed": 0, "total_filtered": 0}
    
    def filter_by_threshold(
        self,
        readings: List[Dict],
        sensor_type: str,
        threshold: float,
        comparison: str = "greater",
    ) -> List[Dict]:
        """
        Filter readings based on threshold.
        
        Args:
            readings: List of sensor readings
            sensor_type: Type of sensor to filter
            threshold: Threshold value
            comparison: 'greater', 'less', 'equal'
            
        Returns:
            Filtered list of readings
        """
        filtered = []
        
        for reading in readings:
            if reading.get("sensor_type") != sensor_type:
                continue
            
            value = reading.get("value", 0)
            
            if comparison == "greater" and value > threshold:
                filtered.append(reading)
            elif comparison == "less" and value < threshold:
                filtered.append(reading)
            elif comparison == "equal" and value == threshold:
                filtered.append(reading)
        
        self.processing_stats["total_filtered"] += len(filtered)
        return filtered
    
    def aggregate_by_machine(
        self,
        readings: List[Dict],
        aggregation: str = "mean",
    ) -> Dict[str, Dict[str, float]]:
        """
        Aggregate readings by machine ID.
        
        Args:
            readings: List of sensor readings
            aggregation: Type of aggregation ('mean', 'min', 'max', 'sum')
            
        Returns:
            Dictionary mapping machine_id to aggregated values by sensor type
        """
        machine_data = {}
        
        for reading in readings:
            machine_id = reading.get("machine_id")
            sensor_type = reading.get("sensor_type")
            value = reading.get("value")
            
            if not all([machine_id, sensor_type, value is not None]):
                continue
            
            if machine_id not in machine_data:
                machine_data[machine_id] = {}
            
            if sensor_type not in machine_data[machine_id]:
                machine_data[machine_id][sensor_type] = []
            
            machine_data[machine_id][sensor_type].append(value)
        
        # Apply aggregation
        result = {}
        for machine_id, sensor_data in machine_data.items():
            result[machine_id] = {}
            for sensor_type, values in sensor_data.items():
                if aggregation == "mean":
                    result[machine_id][sensor_type] = statistics.mean(values)
                elif aggregation == "min":
                    result[machine_id][sensor_type] = min(values)
                elif aggregation == "max":
                    result[machine_id][sensor_type] = max(values)
                elif aggregation == "sum":
                    result[machine_id][sensor_type] = sum(values)
        
        self.processing_stats["total_processed"] += len(readings)
        return result
    
    def detect_anomalies(
        self,
        readings: List[Dict],
        std_threshold: float = 2.0,
    ) -> List[Dict]:
        """
        Detect anomalies using statistical methods.
        
        Args:
            readings: List of sensor readings
            std_threshold: Number of standard deviations for anomaly detection
            
        Returns:
            List of anomalous readings
        """
        # Group by sensor type
        sensor_values = {}
        for reading in readings:
            sensor_type = reading.get("sensor_type")
            value = reading.get("value")
            
            if sensor_type and value is not None:
                if sensor_type not in sensor_values:
                    sensor_values[sensor_type] = []
                sensor_values[sensor_type].append(reading)
        
        # Detect anomalies
        anomalies = []
        for sensor_type, readings_list in sensor_values.items():
            values = [r["value"] for r in readings_list]
            
            if len(values) < 2:
                continue
            
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            
            for reading in readings_list:
                value = reading["value"]
                z_score = abs((value - mean) / stdev) if stdev > 0 else 0
                
                if z_score > std_threshold:
                    reading["anomaly_score"] = z_score
                    anomalies.append(reading)
        
        return anomalies
    
    def enrich_reading(self, reading: Dict, metadata: Dict) -> Dict:
        """
        Enrich reading with additional metadata.
        
        Args:
            reading: Sensor reading
            metadata: Additional metadata to add
            
        Returns:
            Enriched reading
        """
        enriched = reading.copy()
        enriched.update(metadata)
        enriched["processed_at"] = datetime.utcnow().isoformat() + "Z"
        return enriched
    
    def calculate_derived_metrics(self, readings: List[Dict]) -> Dict[str, Any]:
        """
        Calculate derived metrics from readings.
        
        Args:
            readings: List of sensor readings
            
        Returns:
            Dictionary of derived metrics
        """
        if not readings:
            return {}
        
        metrics = {
            "total_readings": len(readings),
            "unique_machines": len(set(r.get("machine_id") for r in readings)),
            "unique_sensors": len(set(r.get("sensor_id") for r in readings)),
            "timestamp_range": {
                "start": min(r.get("timestamp", "") for r in readings),
                "end": max(r.get("timestamp", "") for r in readings),
            },
        }
        
        # Calculate per-sensor-type statistics
        sensor_stats = {}
        for reading in readings:
            sensor_type = reading.get("sensor_type")
            value = reading.get("value")
            
            if sensor_type and value is not None:
                if sensor_type not in sensor_stats:
                    sensor_stats[sensor_type] = []
                sensor_stats[sensor_type].append(value)
        
        for sensor_type, values in sensor_stats.items():
            metrics[f"{sensor_type}_mean"] = statistics.mean(values)
            metrics[f"{sensor_type}_min"] = min(values)
            metrics[f"{sensor_type}_max"] = max(values)
        
        return metrics
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.processing_stats.copy()
