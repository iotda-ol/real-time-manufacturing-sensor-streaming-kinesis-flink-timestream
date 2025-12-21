"""
Data Ingestion Module

Provides classes and utilities for generating and ingesting manufacturing sensor data.
"""

from .data_generator import DataGenerator
from .kinesis_producer import KinesisProducer

__all__ = ["DataGenerator", "KinesisProducer"]
