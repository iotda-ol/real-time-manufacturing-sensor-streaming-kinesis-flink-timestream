"""
Real-Time Manufacturing Sensor Streaming Package

This package provides reusable modules for ingesting, processing, and storing
real-time manufacturing sensor data using AWS services.
"""

__version__ = "1.0.0"
__author__ = "Manufacturing IoT Team"

from python.src.ingestion import DataGenerator, KinesisProducer
from python.src.processing import DataProcessor, DataTransformer
from python.src.storage import TimestreamClient
from python.src.monitoring import MetricsCollector, AlertManager
from python.src.utils import ConfigManager, Logger

__all__ = [
    "DataGenerator",
    "KinesisProducer",
    "DataProcessor",
    "DataTransformer",
    "TimestreamClient",
    "MetricsCollector",
    "AlertManager",
    "ConfigManager",
    "Logger",
]
