# Amazon Kinesis Data Stream for sensor data ingestion
resource "aws_kinesis_stream" "sensor_stream" {
  name             = "${var.project_name}-sensor-stream-${var.environment}"
  shard_count      = var.kinesis_shard_count
  retention_period = var.kinesis_retention_hours

  shard_level_metrics = [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis_key.id

  tags = {
    Name = "${var.project_name}-sensor-stream"
  }
}

# KMS key for Kinesis encryption
resource "aws_kms_key" "kinesis_key" {
  description             = "KMS key for Kinesis Data Stream encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-kinesis-key"
  }
}

resource "aws_kms_alias" "kinesis_key_alias" {
  name          = "alias/${var.project_name}-kinesis-${var.environment}"
  target_key_id = aws_kms_key.kinesis_key.key_id
}
