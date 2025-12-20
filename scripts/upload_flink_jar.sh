#!/bin/bash
set -e

echo "Uploading Flink JAR to S3..."

# Check if outputs file exists
if [ ! -f "$(dirname "$0")/../outputs.json" ]; then
    echo "✗ outputs.json not found. Please deploy infrastructure first."
    exit 1
fi

# Extract S3 bucket name from outputs
S3_BUCKET=$(cat "$(dirname "$0")/../outputs.json" | grep -o '"s3_bucket_name"[^,]*' | cut -d'"' -f4)

if [ -z "$S3_BUCKET" ]; then
    echo "✗ Could not find S3 bucket name in outputs.json"
    exit 1
fi

# Path to JAR file
JAR_FILE="$(dirname "$0")/../src/flink/target/sensor-stream-processor-1.0.0.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "✗ JAR file not found. Please build the Flink application first."
    exit 1
fi

# Upload to S3
echo "Uploading to s3://${S3_BUCKET}/flink-app.jar"
aws s3 cp "$JAR_FILE" "s3://${S3_BUCKET}/flink-app.jar"

echo "✓ Upload successful!"
