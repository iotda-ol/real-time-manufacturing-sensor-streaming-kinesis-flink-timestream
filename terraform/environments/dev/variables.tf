# Variables for Development Environment

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnets"
  type        = bool
  default     = true
}

# Kinesis Configuration
variable "kinesis_stream_name" {
  description = "Name of the Kinesis Data Stream"
  type        = string
  default     = "manufacturing-sensor-stream-dev"
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis stream"
  type        = number
  default     = 2
}

variable "kinesis_retention_hours" {
  description = "Data retention period in hours"
  type        = number
  default     = 24
}

# Timestream Configuration
variable "timestream_database" {
  description = "Timestream database name"
  type        = string
  default     = "manufacturing_db_dev"
}

variable "timestream_table" {
  description = "Timestream table name"
  type        = string
  default     = "sensor_data"
}

variable "timestream_memory_retention_hours" {
  description = "Memory store retention in hours"
  type        = number
  default     = 24
}

variable "timestream_magnetic_retention_days" {
  description = "Magnetic store retention in days"
  type        = number
  default     = 30
}
