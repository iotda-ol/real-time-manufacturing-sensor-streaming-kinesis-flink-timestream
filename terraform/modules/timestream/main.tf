# Timestream Module
#
# Creates and manages Amazon Timestream database and tables

variable "database_name" {
  description = "Name of the Timestream database"
  type        = string
}

variable "table_name" {
  description = "Name of the Timestream table"
  type        = string
}

variable "memory_retention_hours" {
  description = "Memory store retention period in hours"
  type        = number
  default     = 24
}

variable "magnetic_retention_days" {
  description = "Magnetic store retention period in days"
  type        = number
  default     = 365
}

variable "enable_magnetic_store" {
  description = "Enable magnetic store writes"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Timestream Database
resource "aws_timestreamwrite_database" "main" {
  database_name = var.database_name

  tags = merge(
    var.tags,
    {
      Name      = var.database_name
      ManagedBy = "Terraform"
    }
  )
}

# Timestream Table
resource "aws_timestreamwrite_table" "main" {
  database_name = aws_timestreamwrite_database.main.database_name
  table_name    = var.table_name

  retention_properties {
    memory_store_retention_period_in_hours  = var.memory_retention_hours
    magnetic_store_retention_period_in_days = var.magnetic_retention_days
  }

  dynamic "magnetic_store_write_properties" {
    for_each = var.enable_magnetic_store ? [1] : []
    content {
      enable_magnetic_store_writes = true
    }
  }

  tags = merge(
    var.tags,
    {
      Name      = var.table_name
      ManagedBy = "Terraform"
    }
  )
}

# Outputs
output "database_name" {
  description = "Name of the Timestream database"
  value       = aws_timestreamwrite_database.main.database_name
}

output "database_arn" {
  description = "ARN of the Timestream database"
  value       = aws_timestreamwrite_database.main.arn
}

output "table_name" {
  description = "Name of the Timestream table"
  value       = aws_timestreamwrite_table.main.table_name
}

output "table_arn" {
  description = "ARN of the Timestream table"
  value       = aws_timestreamwrite_table.main.arn
}
