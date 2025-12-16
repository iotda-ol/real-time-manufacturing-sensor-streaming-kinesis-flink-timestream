# CloudWatch Log Group for Flink application
resource "aws_cloudwatch_log_group" "flink_app" {
  name              = "/aws/kinesis-analytics/${var.project_name}-sensor-processor-${var.environment}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-flink-logs"
  }
}

resource "aws_cloudwatch_log_stream" "flink_app" {
  name           = "kinesis-analytics-log-stream"
  log_group_name = aws_cloudwatch_log_group.flink_app.name
}

# Amazon Managed Service for Apache Flink Application
resource "aws_kinesisanalyticsv2_application" "sensor_processor" {
  name                   = "${var.project_name}-sensor-processor-${var.environment}"
  runtime_environment    = "FLINK-1_18"
  service_execution_role = aws_iam_role.flink_role.arn

  application_configuration {
    application_code_configuration {
      code_content {
        s3_content_location {
          bucket_arn = aws_s3_bucket.flink_artifacts.arn
          file_key   = "flink-app.jar"
        }
      }

      code_content_type = "ZIPFILE"
    }

    environment_properties {
      property_group {
        property_group_id = "ProducerConfigProperties"

        property_map = {
          "aws.region"            = data.aws_region.current.name
          "timestream.database"   = aws_timestreamwrite_database.manufacturing_db.database_name
          "timestream.table"      = aws_timestreamwrite_table.sensor_metrics.table_name
          "kinesis.stream.name"   = aws_kinesis_stream.sensor_stream.name
        }
      }

      property_group {
        property_group_id = "FlinkApplicationProperties"

        property_map = {
          "checkpoint.interval"     = "60000"
          "min.pause.between.checkpoints" = "5000"
        }
      }
    }

    flink_application_configuration {
      checkpoint_configuration {
        configuration_type = "DEFAULT"
      }

      monitoring_configuration {
        configuration_type = "CUSTOM"
        log_level          = "INFO"
        metrics_level      = "APPLICATION"
      }

      parallelism_configuration {
        configuration_type   = "CUSTOM"
        parallelism          = var.kinesis_shard_count
        parallelism_per_kpu  = 1
        auto_scaling_enabled = true
      }
    }

    application_snapshot_configuration {
      snapshots_enabled = true
    }
  }

  cloudwatch_logging_options {
    log_stream_arn = aws_cloudwatch_log_stream.flink_app.arn
  }

  tags = {
    Name = "${var.project_name}-flink-app"
  }
}
