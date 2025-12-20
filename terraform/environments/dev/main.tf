# Development Environment Terraform Configuration
#
# This deploys the complete infrastructure for the development environment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state management
  # Uncomment and configure after creating the backend resources
  # backend "s3" {
  #   bucket         = "manufacturing-sensor-terraform-state-dev"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "manufacturing-sensor-streaming"
      Environment = "dev"
      ManagedBy   = "Terraform"
      Owner       = "Engineering Team"
    }
  }
}

# Local variables
locals {
  project_name = "manufacturing-sensor-dev"
  environment  = "dev"
  
  common_tags = {
    Project     = "manufacturing-sensor-streaming"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"
  
  project_name         = local.project_name
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.enable_nat_gateway
  
  tags = local.common_tags
}

# S3 Buckets Module
module "s3" {
  source = "../../modules/s3"
  
  project_name      = local.project_name
  environment       = local.environment
  enable_versioning = true
  enable_encryption = true
  
  tags = local.common_tags
}

# Kinesis Data Stream Module
module "kinesis" {
  source = "../../modules/kinesis"
  
  stream_name      = var.kinesis_stream_name
  shard_count      = var.kinesis_shard_count
  retention_period = var.kinesis_retention_hours
  encryption_type  = "KMS"
  
  tags = local.common_tags
}

# Timestream Database and Table Module
module "timestream" {
  source = "../../modules/timestream"
  
  database_name            = var.timestream_database
  table_name               = var.timestream_table
  memory_retention_hours   = var.timestream_memory_retention_hours
  magnetic_retention_days  = var.timestream_magnetic_retention_days
  enable_magnetic_store    = true
  
  tags = local.common_tags
}

# IAM Roles and Policies Module
module "iam" {
  source = "../../modules/iam"
  
  project_name           = local.project_name
  kinesis_stream_arn     = module.kinesis.stream_arn
  timestream_database_arn = module.timestream.database_arn
  timestream_table_arn    = module.timestream.table_arn
  s3_bucket_arn          = module.s3.data_bucket_arn
  
  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "kinesis_stream_name" {
  description = "Kinesis stream name"
  value       = module.kinesis.stream_name
}

output "kinesis_stream_arn" {
  description = "Kinesis stream ARN"
  value       = module.kinesis.stream_arn
}

output "timestream_database_name" {
  description = "Timestream database name"
  value       = module.timestream.database_name
}

output "timestream_table_name" {
  description = "Timestream table name"
  value       = module.timestream.table_name
}

output "s3_data_bucket" {
  description = "S3 data bucket name"
  value       = module.s3.data_bucket_name
}

output "s3_logs_bucket" {
  description = "S3 logs bucket name"
  value       = module.s3.logs_bucket_name
}

output "flink_role_arn" {
  description = "Flink IAM role ARN"
  value       = module.iam.flink_role_arn
}
