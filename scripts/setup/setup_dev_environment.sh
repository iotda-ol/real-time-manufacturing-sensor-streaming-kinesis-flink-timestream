#!/bin/bash
# Setup Script for Development Environment
#
# This script sets up the development environment with all required tools and dependencies.

set -e

echo "=================================="
echo "Development Environment Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.9 or later."
    exit 1
fi

# Check Terraform
echo ""
echo "Checking Terraform installation..."
if command -v terraform &> /dev/null; then
    TERRAFORM_VERSION=$(terraform version | head -n1 | cut -d'v' -f2)
    print_success "Terraform v$TERRAFORM_VERSION found"
else
    print_warning "Terraform not found. Please install Terraform 1.0 or later."
    print_info "Download from: https://www.terraform.io/downloads"
fi

# Check AWS CLI
echo ""
echo "Checking AWS CLI installation..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
    print_success "AWS CLI $AWS_VERSION found"
else
    print_warning "AWS CLI not found. Please install AWS CLI v2."
    print_info "Download from: https://aws.amazon.com/cli/"
fi

# Check Git
echo ""
echo "Checking Git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_success "Git $GIT_VERSION found"
else
    print_error "Git not found. Please install Git."
    exit 1
fi

# Create Python virtual environment
echo ""
echo "Setting up Python virtual environment..."
cd "$(dirname "$0")/../.."

if [ ! -d "python/venv" ]; then
    python3 -m venv python/venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing Python dependencies..."
source python/venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r python/requirements.txt > /dev/null 2>&1
print_success "Python dependencies installed"

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p logs tmp/data tmp/scripts
print_success "Project directories created"

# Check AWS credentials
echo ""
echo "Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS credentials configured (Account: $ACCOUNT_ID)"
else
    print_warning "AWS credentials not configured or invalid"
    print_info "Run 'aws configure' to set up your credentials"
fi

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source python/venv/bin/activate"
echo "2. Configure AWS credentials: aws configure"
echo "3. Review configuration files in config/"
echo "4. Initialize Terraform: cd terraform/environments/dev && terraform init"
echo "5. Follow the tutorial: docs/TUTORIAL_MASTER.md"
echo ""
echo "Happy coding! 🚀"
