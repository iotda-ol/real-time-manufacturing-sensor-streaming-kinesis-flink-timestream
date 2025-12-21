# Kinesis Data Streams Module
#
# Creates and manages Kinesis Data Streams for sensor data ingestion

variable "stream_name" {
  description = "Name of the Kinesis Data Stream"
  type        = string
}

variable "shard_count" {
  description = "Number of shards for the stream"
  type        = number
  default     = 2
}

variable "retention_period" {
  description = "Data retention period in hours (24-8760)"
  type        = number
  default     = 24
}

variable "encryption_type" {
  description = "Encryption type (KMS or NONE)"
  type        = string
  default     = "KMS"
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (optional)"
  type        = string
  default     = null
}

variable "shard_level_metrics" {
  description = "List of shard-level metrics to enable"
  type        = list(string)
  default = [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
  ]
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Kinesis Data Stream
resource "aws_kinesis_stream" "main" {
  name             = var.stream_name
  shard_count      = var.shard_count
  retention_period = var.retention_period

  encryption_type = var.encryption_type
  kms_key_id      = var.kms_key_id

  shard_level_metrics = var.shard_level_metrics

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = merge(
    var.tags,
    {
      Name        = var.stream_name
      ManagedBy   = "Terraform"
      Purpose     = "Manufacturing sensor data ingestion"
    }
  )
}

# CloudWatch Log Group for Kinesis
resource "aws_cloudwatch_log_group" "kinesis" {
  name              = "/aws/kinesis/${var.stream_name}"
  retention_in_days = 7

  tags = var.tags
}

# Outputs
output "stream_name" {
  description = "Name of the Kinesis stream"
  value       = aws_kinesis_stream.main.name
}

output "stream_arn" {
  description = "ARN of the Kinesis stream"
  value       = aws_kinesis_stream.main.arn
}

output "shard_count" {
  description = "Number of shards in the stream"
  value       = aws_kinesis_stream.main.shard_count
}
