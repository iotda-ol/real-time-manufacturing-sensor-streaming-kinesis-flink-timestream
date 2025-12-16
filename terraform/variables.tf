variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, prod, etc.)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "manufacturing-analytics"
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis Data Stream"
  type        = number
  default     = 2
}

variable "kinesis_retention_hours" {
  description = "Data retention period in hours for Kinesis"
  type        = number
  default     = 24
}

variable "timestream_memory_retention_hours" {
  description = "Memory store retention period in hours"
  type        = number
  default     = 24
}

variable "timestream_magnetic_retention_days" {
  description = "Magnetic store retention period in days"
  type        = number
  default     = 90
}

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}
