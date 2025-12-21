#!/usr/bin/env python3
"""
End-to-End Example: Data Ingestion Pipeline

This script demonstrates the complete data ingestion pipeline:
1. Generate sensor data
2. Send to Kinesis Data Streams
3. Verify data arrival

Usage:
    python e2e_ingestion_example.py --stream-name STREAM_NAME --num-records 100
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from python.src.ingestion import DataGenerator, KinesisProducer
from python.src.utils import Logger


def main():
    """Run end-to-end ingestion example."""
    parser = argparse.ArgumentParser(description="E2E Data Ingestion Example")
    parser.add_argument(
        "--stream-name",
        default="manufacturing-sensor-stream-dev",
        help="Kinesis stream name"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region"
    )
    parser.add_argument(
        "--num-records",
        type=int,
        default=100,
        help="Number of records to generate"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for sending records"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Interval between batches (seconds)"
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = Logger("e2e-ingestion", level="INFO")
    
    logger.info("=" * 60)
    logger.info("Starting E2E Data Ingestion Example")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("Initializing components...")
    generator = DataGenerator(
        num_machines=5,
        sensors_per_machine=4,
        location="Factory-Example"
    )
    
    producer = KinesisProducer(
        stream_name=args.stream_name,
        region_name=args.region,
        logger=logger.get_logger()
    )
    
    logger.info(f"Stream: {args.stream_name}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Total records to generate: {args.num_records}")
    
    # Generate and send data
    total_sent = 0
    total_failed = 0
    
    try:
        while total_sent < args.num_records:
            # Generate batch
            batch_size = min(args.batch_size, args.num_records - total_sent)
            readings = generator.generate_batch(batch_size)
            
            logger.info(f"Generated {len(readings)} sensor readings")
            
            # Send to Kinesis
            results = producer.put_sensor_readings(readings)
            
            total_sent += results["success"]
            total_failed += results["failed"]
            
            logger.info(
                f"Progress: {total_sent}/{args.num_records} sent, "
                f"{total_failed} failed"
            )
            
            # Wait before next batch
            if total_sent < args.num_records:
                time.sleep(args.interval)
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
    
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("Ingestion Complete")
    logger.info("=" * 60)
    logger.info(f"Total records sent: {total_sent}")
    logger.info(f"Total records failed: {total_failed}")
    logger.info(f"Success rate: {total_sent / args.num_records * 100:.1f}%")
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
