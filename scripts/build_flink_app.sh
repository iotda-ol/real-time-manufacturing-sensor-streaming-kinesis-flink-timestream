#!/bin/bash
set -e

echo "Building Flink Application..."

# Navigate to Flink source directory
cd "$(dirname "$0")/../src/flink"

# Build with Maven
mvn clean package -DskipTests

# Check if build was successful
if [ -f target/sensor-stream-processor-1.0.0.jar ]; then
    echo "✓ Build successful!"
    echo "JAR location: $(pwd)/target/sensor-stream-processor-1.0.0.jar"
else
    echo "✗ Build failed!"
    exit 1
fi
