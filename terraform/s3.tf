# S3 bucket for Flink application artifacts
resource "aws_s3_bucket" "flink_artifacts" {
  bucket = "${var.project_name}-flink-artifacts-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.project_name}-flink-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "flink_artifacts" {
  bucket = aws_s3_bucket.flink_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "flink_artifacts" {
  bucket = aws_s3_bucket.flink_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_key.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "flink_artifacts" {
  bucket = aws_s3_bucket.flink_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket for rejected Timestream data
resource "aws_s3_bucket" "rejected_data" {
  bucket = "${var.project_name}-rejected-data-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.project_name}-rejected-data"
  }
}

resource "aws_s3_bucket_versioning" "rejected_data" {
  bucket = aws_s3_bucket.rejected_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "rejected_data" {
  bucket = aws_s3_bucket.rejected_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_key.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "rejected_data" {
  bucket = aws_s3_bucket.rejected_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "rejected_data" {
  bucket = aws_s3_bucket.rejected_data.id

  rule {
    id     = "delete-old-rejected-data"
    status = "Enabled"

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# KMS key for S3 encryption
resource "aws_kms_key" "s3_key" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-s3-key"
  }
}

resource "aws_kms_alias" "s3_key_alias" {
  name          = "alias/${var.project_name}-s3-${var.environment}"
  target_key_id = aws_kms_key.s3_key.key_id
}
