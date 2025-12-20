# IAM role for Flink application
resource "aws_iam_role" "flink_role" {
  name = "${var.project_name}-flink-role-${var.environment}"

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

  tags = {
    Name = "${var.project_name}-flink-role"
  }
}

# Policy for Flink to read from Kinesis
resource "aws_iam_role_policy" "flink_kinesis_policy" {
  name = "kinesis-read-policy"
  role = aws_iam_role.flink_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards"
        ]
        Resource = aws_kinesis_stream.sensor_stream.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStreamSummary",
          "kinesis:ListStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# Policy for Flink to write to Timestream
resource "aws_iam_role_policy" "flink_timestream_policy" {
  name = "timestream-write-policy"
  role = aws_iam_role.flink_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:WriteRecords",
          "timestream:DescribeEndpoints"
        ]
        Resource = aws_timestreamwrite_table.sensor_metrics.arn
      },
      {
        Effect = "Allow"
        Action = [
          "timestream:DescribeEndpoints"
        ]
        Resource = "*"
      }
    ]
  })
}

# Policy for Flink to access S3 artifacts
resource "aws_iam_role_policy" "flink_s3_policy" {
  name = "s3-artifacts-policy"
  role = aws_iam_role.flink_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.flink_artifacts.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.flink_artifacts.arn
      }
    ]
  })
}

# Policy for Flink CloudWatch Logs
resource "aws_iam_role_policy" "flink_cloudwatch_policy" {
  name = "cloudwatch-logs-policy"
  role = aws_iam_role.flink_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/kinesis-analytics/${var.project_name}-*"
      }
    ]
  })
}

# Policy for KMS key usage
resource "aws_iam_role_policy" "flink_kms_policy" {
  name = "kms-policy"
  role = aws_iam_role.flink_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.kinesis_key.arn,
          aws_kms_key.s3_key.arn
        ]
      }
    ]
  })
}

# IAM role for data generator (Lambda or EC2)
resource "aws_iam_role" "data_generator_role" {
  name = "${var.project_name}-data-generator-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.amazonaws.com",
            "ec2.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-data-generator-role"
  }
}

# Policy for data generator to write to Kinesis
resource "aws_iam_role_policy" "data_generator_kinesis_policy" {
  name = "kinesis-write-policy"
  role = aws_iam_role.data_generator_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:PutRecord",
          "kinesis:PutRecords",
          "kinesis:DescribeStream"
        ]
        Resource = aws_kinesis_stream.sensor_stream.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt"
        ]
        Resource = aws_kms_key.kinesis_key.arn
      }
    ]
  })
}

# CloudWatch Logs policy for data generator
resource "aws_iam_role_policy" "data_generator_logs_policy" {
  name = "cloudwatch-logs-policy"
  role = aws_iam_role.data_generator_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/${var.project_name}/*"
      }
    ]
  })
}

# IAM role for Grafana to query Timestream
resource "aws_iam_role" "grafana_role" {
  name = "${var.project_name}-grafana-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "grafana.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-grafana-role"
  }
}

# Policy for Grafana to read from Timestream
resource "aws_iam_role_policy" "grafana_timestream_policy" {
  name = "timestream-read-policy"
  role = aws_iam_role.grafana_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:Select",
          "timestream:DescribeTable",
          "timestream:ListMeasures"
        ]
        Resource = [
          aws_timestreamwrite_database.manufacturing_db.arn,
          aws_timestreamwrite_table.sensor_metrics.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "timestream:DescribeEndpoints",
          "timestream:ListDatabases",
          "timestream:ListTables"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.timestream_key.arn
      }
    ]
  })
}
