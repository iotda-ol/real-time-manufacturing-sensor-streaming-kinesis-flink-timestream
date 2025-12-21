#!/bin/bash
set -e

echo "Starting Sensor Data Generator..."

# Check if outputs file exists
if [ ! -f "$(dirname "$0")/../outputs.json" ]; then
    echo "✗ outputs.json not found. Please deploy infrastructure first."
    exit 1
fi

# Extract Kinesis stream name from outputs
STREAM_NAME=$(cat "$(dirname "$0")/../outputs.json" | grep -o '"kinesis_stream_name"[^,]*' | cut -d'"' -f4)

if [ -z "$STREAM_NAME" ]; then
    echo "✗ Could not find Kinesis stream name in outputs.json"
    exit 1
fi

# Install Python dependencies if not already installed
if [ ! -d "$(dirname "$0")/../src/data_generator/venv" ]; then
    echo "Creating Python virtual environment..."
    cd "$(dirname "$0")/../src/data_generator"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Using existing virtual environment..."
    cd "$(dirname "$0")/../src/data_generator"
    source venv/bin/activate
fi

# Start data generator
echo "Starting data generator for stream: $STREAM_NAME"
python sensor_data_generator.py --stream-name "$STREAM_NAME" --region us-east-1
