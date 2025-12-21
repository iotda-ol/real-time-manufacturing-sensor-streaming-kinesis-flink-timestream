output "kinesis_stream_name" {
  description = "Name of the Kinesis Data Stream"
  value       = aws_kinesis_stream.sensor_stream.name
}

output "kinesis_stream_arn" {
  description = "ARN of the Kinesis Data Stream"
  value       = aws_kinesis_stream.sensor_stream.arn
}

output "timestream_database_name" {
  description = "Name of the Timestream database"
  value       = aws_timestreamwrite_database.manufacturing_db.database_name
}

output "timestream_table_name" {
  description = "Name of the Timestream table"
  value       = aws_timestreamwrite_table.sensor_metrics.table_name
}

output "flink_application_name" {
  description = "Name of the Flink application"
  value       = aws_kinesisanalyticsv2_application.sensor_processor.name
}

output "flink_application_arn" {
  description = "ARN of the Flink application"
  value       = aws_kinesisanalyticsv2_application.sensor_processor.arn
}

output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.manufacturing_dashboard.dashboard_name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Flink artifacts"
  value       = aws_s3_bucket.flink_artifacts.id
}
