#!/bin/bash
set -e

echo "Deploying Infrastructure with Terraform..."

# Navigate to Terraform directory
cd "$(dirname "$0")/../terraform"

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

# Plan infrastructure changes
echo "Planning infrastructure changes..."
terraform plan -out=tfplan

# Apply infrastructure changes
echo "Applying infrastructure changes..."
read -p "Do you want to apply these changes? (yes/no) " -n 3 -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]
then
    terraform apply tfplan
    echo "✓ Infrastructure deployed successfully!"
    
    # Save outputs
    terraform output -json > ../outputs.json
    echo "✓ Outputs saved to outputs.json"
else
    echo "Deployment cancelled"
    exit 1
fi
