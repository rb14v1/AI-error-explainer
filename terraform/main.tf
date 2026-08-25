# =============================================================================
# AI Error Explainer — Production Database (RDS PostgreSQL)
# =============================================================================
# This Terraform configuration provisions:
#   • An AWS RDS PostgreSQL instance in the primary region
#   • Automated backups with a 30-day retention window
#   • Point-In-Time Recovery (PITR) — enabled by default on RDS when
#     backup_retention_period > 0
#   • Cross-region automated backup replication to a secondary region via the
#     aws_db_instance_automated_backups_replication resource
#
# See docs/backup-and-restore.md for the documented restore procedure.
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "primary_region" {
  description = "AWS region where the primary RDS instance runs."
  type        = string
  default     = "eu-west-1"
}

variable "replica_region" {
  description = "AWS region where cross-region backup copies are stored."
  type        = string
  default     = "eu-west-2"
}

variable "db_identifier" {
  description = "Unique identifier for the RDS instance."
  type        = string
  default     = "ai-error-explainer-db"
}

variable "db_name" {
  description = "Name of the initial database to create."
  type        = string
  default     = "ai_error_explainer"
}

variable "db_username" {
  description = "Master username for the RDS instance."
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_password" {
  description = "Master password for the RDS instance. Supply via TF_VAR_db_password or -var flag."
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "backup_retention_days" {
  description = "Number of days to retain automated backups (minimum 30 for compliance)."
  type        = number
  default     = 30

  validation {
    condition     = var.backup_retention_days >= 30
    error_message = "backup_retention_days must be at least 30 to satisfy the backup compliance requirement."
  }
}

variable "backup_window" {
  description = "Preferred UTC backup window (hh24:mi-hh24:mi)."
  type        = string
  default     = "02:00-03:00"
}

variable "maintenance_window" {
  description = "Preferred UTC maintenance window."
  type        = string
  default     = "mon:04:00-mon:05:00"
}

# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

provider "aws" {
  region = var.primary_region
  alias  = "primary"
}

provider "aws" {
  region = var.replica_region
  alias  = "replica"
}

# ---------------------------------------------------------------------------
# Networking (attach to default VPC)
# ---------------------------------------------------------------------------

data "aws_vpc" "default" {
  provider = aws.primary
  default  = true
}

data "aws_subnets" "default" {
  provider = aws.primary
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "main" {
  provider   = aws.primary
  name       = "${var.db_identifier}-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name        = "${var.db_identifier}-subnet-group"
    Application = "ai-error-explainer"
    ManagedBy   = "Terraform"
  }
}

resource "aws_security_group" "rds" {
  provider    = aws.primary
  name        = "${var.db_identifier}-sg"
  description = "Allow PostgreSQL access from application layer only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL from within the VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.db_identifier}-sg"
    Application = "ai-error-explainer"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# RDS PostgreSQL — Primary instance
# ---------------------------------------------------------------------------

resource "aws_db_instance" "primary" {
  provider   = aws.primary
  identifier = var.db_identifier

  # Engine
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  # Storage
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  # Credentials
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # ---------------------------------------------------------------------------
  # Backup & PITR — core compliance settings
  # ---------------------------------------------------------------------------
  # Setting backup_retention_period > 0 enables both automated daily snapshots
  # AND Point-In-Time Recovery (PITR) on AWS RDS.  The minimum required
  # retention is 30 days, enforced by the variable validation above.
  backup_retention_period  = var.backup_retention_days
  backup_window            = var.backup_window
  delete_automated_backups = false  # retain backups even after instance deletion
  copy_tags_to_snapshot    = true
  skip_final_snapshot      = false
  final_snapshot_identifier = "${var.db_identifier}-final-snapshot"

  # Maintenance
  maintenance_window         = var.maintenance_window
  auto_minor_version_upgrade = true
  apply_immediately          = false

  # High availability
  multi_az = true

  tags = {
    Name                = var.db_identifier
    Application         = "ai-error-explainer"
    ManagedBy           = "Terraform"
    BackupRetentionDays = tostring(var.backup_retention_days)
    PITREnabled         = "true"
  }
}

# ---------------------------------------------------------------------------
# Cross-region automated backup replication
# ---------------------------------------------------------------------------
# Replicates automated backups to the replica region so that backups are
# stored in a separate region from the primary database, satisfying the
# cross-region storage requirement.

resource "aws_db_instance_automated_backups_replication" "cross_region" {
  provider               = aws.replica
  source_db_instance_arn = aws_db_instance.primary.arn
  retention_period       = var.backup_retention_days
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "db_endpoint" {
  description = "RDS instance endpoint (host:port)."
  value       = aws_db_instance.primary.endpoint
  sensitive   = true
}

output "db_name" {
  description = "Database name."
  value       = aws_db_instance.primary.db_name
}

output "db_arn" {
  description = "ARN of the RDS instance (used for restore operations)."
  value       = aws_db_instance.primary.arn
}

output "replica_region" {
  description = "AWS region storing cross-region backup copies."
  value       = var.replica_region
}
