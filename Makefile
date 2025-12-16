.PHONY: help build deploy upload start-flink start-generator clean validate

# Default target
help:
	@echo "Manufacturing Analytics Platform - Available Commands:"
	@echo ""
	@echo "  make build              - Build Flink application JAR"
	@echo "  make validate          - Validate Terraform configuration"
	@echo "  make plan              - Plan infrastructure changes"
	@echo "  make deploy            - Deploy infrastructure with Terraform"
	@echo "  make upload            - Upload Flink JAR to S3"
	@echo "  make start-flink       - Start Flink application"
	@echo "  make start-generator   - Start sensor data generator"
	@echo "  make logs              - Tail Flink application logs"
	@echo "  make query             - Query Timestream for sample data"
	@echo "  make clean             - Clean build artifacts"
	@echo "  make destroy           - Destroy all infrastructure (WARNING: deletes data)"
	@echo ""

# Build Flink application
build:
	@echo "Building Flink application..."
	cd src/flink && mvn clean package
	@echo "✓ Build complete: src/flink/target/sensor-stream-processor-1.0.0.jar"

# Validate Terraform configuration
validate:
	@echo "Validating Terraform configuration..."
	cd terraform && terraform init -upgrade && terraform validate
	@echo "✓ Validation complete"

# Plan infrastructure changes
plan:
	@echo "Planning infrastructure changes..."
	cd terraform && terraform plan -out=tfplan

# Deploy infrastructure
deploy:
	@echo "Deploying infrastructure..."
	cd terraform && terraform init && terraform apply
	cd terraform && terraform output -json > ../outputs.json
	@echo "✓ Infrastructure deployed successfully"

# Upload Flink JAR to S3
upload:
	@echo "Uploading Flink JAR to S3..."
	@bash scripts/upload_flink_jar.sh

# Start Flink application
start-flink:
	@echo "Starting Flink application..."
	@FLINK_APP_NAME=$$(cat outputs.json | grep -o '"flink_application_name"[^,]*' | cut -d'"' -f4); \
	aws kinesisanalyticsv2 start-application \
		--application-name $$FLINK_APP_NAME \
		--run-configuration '{}'
	@echo "✓ Flink application starting (this may take 2-3 minutes)..."

# Start data generator
start-generator:
	@echo "Starting sensor data generator..."
	@bash scripts/start_data_generator.sh

# View Flink logs
logs:
	@echo "Tailing Flink application logs..."
	@aws logs tail /aws/kinesis-analytics/manufacturing-analytics-sensor-processor-dev \
		--follow --format short

# Query Timestream
query:
	@echo "Querying Timestream for recent data..."
	@DATABASE_NAME=$$(cat outputs.json | grep -o '"timestream_database_name"[^,]*' | cut -d'"' -f4); \
	TABLE_NAME=$$(cat outputs.json | grep -o '"timestream_table_name"[^,]*' | cut -d'"' -f4); \
	aws timestream-query query \
		--query-string "SELECT * FROM \"$$DATABASE_NAME\".\"$$TABLE_NAME\" ORDER BY time DESC LIMIT 10"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cd src/flink && mvn clean
	rm -rf src/data_generator/venv
	rm -f outputs.json
	@echo "✓ Clean complete"

# Destroy infrastructure
destroy:
	@echo "WARNING: This will destroy all infrastructure and delete data!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		cd terraform && terraform destroy; \
		echo "✓ Infrastructure destroyed"; \
	else \
		echo "Cancelled"; \
	fi

# Full deployment
all: build deploy upload start-flink
	@echo "✓ Full deployment complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make start-generator' to generate sensor data"
	@echo "  2. Run 'make logs' to view processing logs"
	@echo "  3. Run 'make query' to verify data in Timestream"
	@echo "  4. Set up Grafana dashboards for visualization"
