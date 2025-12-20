# IAM Module
#
# Creates IAM roles and policies for all services

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "kinesis_stream_arn" {
  description = "ARN of the Kinesis stream"
  type        = string
}

variable "timestream_database_arn" {
  description = "ARN of the Timestream database"
  type        = string
}

variable "timestream_table_arn" {
  description = "ARN of the Timestream table"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
  default     = "*"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Flink Application IAM Role
resource "aws_iam_role" "flink_app" {
  name = "${var.project_name}-flink-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "kinesisanalytics.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

# Flink Policy for Kinesis Access
resource "aws_iam_role_policy" "flink_kinesis" {
  name = "${var.project_name}-flink-kinesis-policy"
  role = aws_iam_role.flink_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards",
        ]
        Resource = var.kinesis_stream_arn
      }
    ]
  })
}

# Flink Policy for Timestream Access
resource "aws_iam_role_policy" "flink_timestream" {
  name = "${var.project_name}-flink-timestream-policy"
  role = aws_iam_role.flink_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:WriteRecords",
          "timestream:DescribeEndpoints",
        ]
        Resource = [
          var.timestream_database_arn,
          var.timestream_table_arn,
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "timestream:DescribeEndpoints",
        ]
        Resource = "*"
      }
    ]
  })
}

# Flink Policy for CloudWatch Logs
resource "aws_iam_role_policy" "flink_cloudwatch" {
  name = "${var.project_name}-flink-cloudwatch-policy"
  role = aws_iam_role.flink_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/flink/*"
      }
    ]
  })
}

# Flink Policy for S3 Access
resource "aws_iam_role_policy" "flink_s3" {
  name = "${var.project_name}-flink-s3-policy"
  role = aws_iam_role.flink_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket",
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*",
        ]
      }
    ]
  })
}

# EC2 Role for Grafana (if using EC2)
resource "aws_iam_role" "grafana" {
  name = "${var.project_name}-grafana-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

# Grafana Policy for Timestream Read Access
resource "aws_iam_role_policy" "grafana_timestream" {
  name = "${var.project_name}-grafana-timestream-policy"
  role = aws_iam_role.grafana.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:DescribeEndpoints",
          "timestream:SelectValues",
          "timestream:DescribeDatabase",
          "timestream:DescribeTable",
          "timestream:ListDatabases",
          "timestream:ListTables",
          "timestream:ListMeasures",
        ]
        Resource = "*"
      }
    ]
  })
}

# Instance Profile for Grafana EC2
resource "aws_iam_instance_profile" "grafana" {
  name = "${var.project_name}-grafana-profile"
  role = aws_iam_role.grafana.name

  tags = var.tags
}

# Outputs
output "flink_role_arn" {
  description = "ARN of the Flink application IAM role"
  value       = aws_iam_role.flink_app.arn
}

output "flink_role_name" {
  description = "Name of the Flink application IAM role"
  value       = aws_iam_role.flink_app.name
}

output "grafana_role_arn" {
  description = "ARN of the Grafana IAM role"
  value       = aws_iam_role.grafana.arn
}

output "grafana_instance_profile_name" {
  description = "Name of the Grafana instance profile"
  value       = aws_iam_instance_profile.grafana.name
}
