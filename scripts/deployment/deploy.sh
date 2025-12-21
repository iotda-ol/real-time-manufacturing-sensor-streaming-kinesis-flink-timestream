#!/bin/bash
# Deployment Script for Development Environment
#
# This script automates the deployment of the complete infrastructure.

set -e

echo "=================================="
echo "Infrastructure Deployment"
echo "=================================="
echo ""

# Configuration
ENVIRONMENT=${1:-dev}
TERRAFORM_DIR="terraform/environments/$ENVIRONMENT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Check if environment exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    print_error "Environment directory not found: $TERRAFORM_DIR"
    exit 1
fi

echo "Environment: $ENVIRONMENT"
echo "Terraform directory: $TERRAFORM_DIR"
echo ""

# Change to terraform directory
cd "$TERRAFORM_DIR"

# Initialize Terraform
echo "Step 1: Initializing Terraform..."
if terraform init; then
    print_success "Terraform initialized"
else
    print_error "Terraform initialization failed"
    exit 1
fi

echo ""

# Validate configuration
echo "Step 2: Validating Terraform configuration..."
if terraform validate; then
    print_success "Configuration is valid"
else
    print_error "Configuration validation failed"
    exit 1
fi

echo ""

# Format code
echo "Step 3: Formatting Terraform code..."
terraform fmt -recursive
print_success "Code formatted"

echo ""

# Plan
echo "Step 4: Creating deployment plan..."
if terraform plan -out=tfplan; then
    print_success "Plan created successfully"
else
    print_error "Plan creation failed"
    exit 1
fi

echo ""

# Confirm deployment
echo "=================================="
read -p "Do you want to apply this plan? (yes/no): " CONFIRM
echo ""

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Deployment cancelled"
    rm -f tfplan
    exit 0
fi

# Apply
echo "Step 5: Applying infrastructure changes..."
if terraform apply tfplan; then
    print_success "Infrastructure deployed successfully"
else
    print_error "Deployment failed"
    exit 1
fi

# Cleanup
rm -f tfplan

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Verify resources in AWS Console"
echo "2. Test data ingestion with examples/python/e2e_ingestion_example.py"
echo "3. Monitor with CloudWatch"
echo ""
