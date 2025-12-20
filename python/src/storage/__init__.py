"""
Storage Module

Provides clients for interacting with AWS Timestream and other storage services.
"""

from .timestream_client import TimestreamClient

__all__ = ["TimestreamClient"]
