# SNS Topic for CloudWatch Alarms
resource "aws_sns_topic" "alarms" {
  name              = "${var.project_name}-alarms-${var.environment}"
  kms_master_key_id = aws_kms_key.sns_key.id

  tags = {
    Name = "${var.project_name}-alarm-topic"
  }
}

resource "aws_sns_topic_subscription" "alarm_email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# KMS key for SNS encryption
resource "aws_kms_key" "sns_key" {
  description             = "KMS key for SNS topic encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch to use the key"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-sns-key"
  }
}

# CloudWatch Alarm for Kinesis Iterator Age
resource "aws_cloudwatch_metric_alarm" "kinesis_iterator_age" {
  alarm_name          = "${var.project_name}-kinesis-iterator-age-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "GetRecords.IteratorAgeMilliseconds"
  namespace           = "AWS/Kinesis"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "60000" # 1 minute
  alarm_description   = "Kinesis iterator age is too high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    StreamName = aws_kinesis_stream.sensor_stream.name
  }

  tags = {
    Name = "${var.project_name}-kinesis-iterator-alarm"
  }
}

# CloudWatch Alarm for Kinesis Incoming Records
resource "aws_cloudwatch_metric_alarm" "kinesis_no_incoming_records" {
  alarm_name          = "${var.project_name}-kinesis-no-records-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "IncomingRecords"
  namespace           = "AWS/Kinesis"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "No records received in Kinesis stream"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    StreamName = aws_kinesis_stream.sensor_stream.name
  }

  tags = {
    Name = "${var.project_name}-kinesis-no-records-alarm"
  }
}

# CloudWatch Alarm for Flink Application Downtime
resource "aws_cloudwatch_metric_alarm" "flink_downtime" {
  alarm_name          = "${var.project_name}-flink-downtime-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "uptime"
  namespace           = "AWS/KinesisAnalytics"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "Flink application is down"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    Application = aws_kinesisanalyticsv2_application.sensor_processor.name
  }

  tags = {
    Name = "${var.project_name}-flink-downtime-alarm"
  }
}

# CloudWatch Alarm for Flink Checkpoint Failures
resource "aws_cloudwatch_metric_alarm" "flink_checkpoint_failure" {
  alarm_name          = "${var.project_name}-flink-checkpoint-failure-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "numFailedCheckpoints"
  namespace           = "AWS/KinesisAnalytics"
  period              = "300"
  statistic           = "Sum"
  threshold           = "2"
  alarm_description   = "Flink application checkpoint failures detected"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    Application = aws_kinesisanalyticsv2_application.sensor_processor.name
  }

  tags = {
    Name = "${var.project_name}-flink-checkpoint-alarm"
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "manufacturing_dashboard" {
  dashboard_name = "${var.project_name}-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Kinesis", "IncomingRecords", { stat = "Sum", label = "Incoming Records" }],
            [".", "IncomingBytes", { stat = "Sum", label = "Incoming Bytes" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Kinesis Stream Metrics"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Kinesis", "GetRecords.IteratorAgeMilliseconds", { stat = "Maximum", label = "Iterator Age" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Kinesis Iterator Age"
          period  = 300
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/KinesisAnalytics", "uptime", { stat = "Average", label = "Uptime" }],
            [".", "downtime", { stat = "Average", label = "Downtime" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Flink Application Status"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/KinesisAnalytics", "numRecordsInPerSecond", { stat = "Average", label = "Records In/Sec" }],
            [".", "numRecordsOutPerSecond", { stat = "Average", label = "Records Out/Sec" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Flink Throughput"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/KinesisAnalytics", "lastCheckpointDuration", { stat = "Average", label = "Checkpoint Duration" }],
            [".", "lastCheckpointSize", { stat = "Average", label = "Checkpoint Size" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Flink Checkpoints"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/KinesisAnalytics", "cpuUtilization", { stat = "Average", label = "CPU Utilization" }],
            [".", "heapMemoryUtilization", { stat = "Average", label = "Heap Memory Utilization" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Flink Resource Utilization"
          period  = 300
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      }
    ]
  })
}
