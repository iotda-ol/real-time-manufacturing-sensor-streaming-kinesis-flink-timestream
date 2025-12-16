# Amazon Timestream Database
resource "aws_timestreamwrite_database" "manufacturing_db" {
  database_name = "${var.project_name}-db-${var.environment}"

  kms_key_id = aws_kms_key.timestream_key.arn

  tags = {
    Name = "${var.project_name}-database"
  }
}

# Amazon Timestream Table for sensor metrics
resource "aws_timestreamwrite_table" "sensor_metrics" {
  database_name = aws_timestreamwrite_database.manufacturing_db.database_name
  table_name    = "sensor_metrics"

  retention_properties {
    memory_store_retention_period_in_hours  = var.timestream_memory_retention_hours
    magnetic_store_retention_period_in_days = var.timestream_magnetic_retention_days
  }

  magnetic_store_write_properties {
    enable_magnetic_store_writes = true

    magnetic_store_rejected_data_location {
      s3_configuration {
        bucket_name       = aws_s3_bucket.rejected_data.id
        encryption_option = "SSE_KMS"
        kms_key_id        = aws_kms_key.s3_key.arn
      }
    }
  }

  tags = {
    Name = "${var.project_name}-sensor-metrics"
  }
}

# KMS key for Timestream encryption
resource "aws_kms_key" "timestream_key" {
  description             = "KMS key for Timestream encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-timestream-key"
  }
}

resource "aws_kms_alias" "timestream_key_alias" {
  name          = "alias/${var.project_name}-timestream-${var.environment}"
  target_key_id = aws_kms_key.timestream_key.key_id
}
