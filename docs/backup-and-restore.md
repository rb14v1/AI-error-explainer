# Database Backup & Restore Procedure

## Overview

The AI Error Explainer production database is an **AWS RDS PostgreSQL** instance
provisioned by Terraform (`terraform/main.tf`).  AWS RDS provides two complementary
backup mechanisms, both enabled by the Terraform configuration:

| Mechanism | What it covers | Retention |
|-----------|---------------|-----------|
| Automated daily snapshots | Full database snapshot taken once per day during the backup window (`02:00–03:00 UTC`) | 30 days |
| Point-In-Time Recovery (PITR) | Transaction-log-based recovery to any second within the retention window | 30 days |

Automated backups are **replicated to a secondary AWS region** (`eu-west-2`) via
`aws_db_instance_automated_backups_replication`, satisfying the requirement for
cross-region storage.

---

## Backup Configuration Summary

| Setting | Value |
|---------|-------|
| Engine | PostgreSQL 16 |
| `backup_retention_period` | 30 days (minimum; increase via `backup_retention_days` Terraform variable) |
| `backup_window` | `02:00–03:00 UTC` daily |
| `delete_automated_backups` | `false` (backups survive instance deletion) |
| `storage_encrypted` | `true` (AES-256 at rest) |
| `multi_az` | `true` (synchronous standby in the same region) |
| Primary region | `eu-west-1` |
| Backup replica region | `eu-west-2` |
| PITR | Enabled automatically (RDS enables PITR whenever `backup_retention_period > 0`) |

---

## Restore Procedures

### 1. Point-In-Time Restore (PITR)

Use this to recover from data corruption or accidental deletion where you need to
restore to an exact moment in time.

**Via AWS Console**

1. Open **RDS → Databases** in the AWS Console.
2. Select the instance `ai-error-explainer-db`.
3. Choose **Actions → Restore to point in time**.
4. Set **Restore time** to the desired UTC timestamp.
5. Provide a new **DB instance identifier** (e.g. `ai-error-explainer-db-pitr`).
6. Confirm all other settings (VPC, security group, parameter group) match the
   source instance, then choose **Restore DB instance**.
7. Wait for the status to reach **Available** (typically 10–20 minutes).
8. Update the `DATABASE_URL` environment variable in the application to point to
   the new instance endpoint, then restart the Django application.
9. Verify data integrity by running `python manage.py check` and spot-checking
   key database tables.
10. Once validated, rename or replace the original instance as required.

**Via AWS CLI**

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier ai-error-explainer-db \
  --target-db-instance-identifier ai-error-explainer-db-pitr \
  --restore-time 2026-08-25T03:00:00Z \
  --db-instance-class db.t3.micro \
  --region eu-west-1
```

---

### 2. Restore from a Daily Automated Snapshot

Use this to restore the full database to the state captured in a specific daily
snapshot.

**List available snapshots**

```bash
aws rds describe-db-snapshots \
  --db-instance-identifier ai-error-explainer-db \
  --snapshot-type automated \
  --region eu-west-1 \
  --query "DBSnapshots[*].{ID:DBSnapshotIdentifier,Time:SnapshotCreateTime,Status:Status}" \
  --output table
```

**Restore from snapshot**

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-error-explainer-db-restored \
  --db-snapshot-identifier <snapshot-identifier> \
  --db-instance-class db.t3.micro \
  --region eu-west-1
```

Then follow steps 7–10 from the PITR procedure above.

---

### 3. Restore from Cross-Region Backup Replica

Use this when the primary region (`eu-west-1`) is unavailable.

**List replicated backups in the replica region**

```bash
aws rds describe-db-instance-automated-backups \
  --region eu-west-2 \
  --query "DBInstanceAutomatedBackups[?DBInstanceIdentifier=='ai-error-explainer-db']"
```

**Restore in the replica region**

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-automated-backups-arn <replicated-backup-arn> \
  --target-db-instance-identifier ai-error-explainer-db-dr \
  --restore-time <ISO-8601-UTC-timestamp> \
  --db-instance-class db.t3.micro \
  --region eu-west-2
```

Update the `DATABASE_URL` environment variable to point to the new endpoint in
`eu-west-2` and redeploy the application in that region.

---

## Pre-Go-Live Restore Test Checklist

The following steps must be executed and signed off **before the first production
go-live**:

- [ ] **Trigger a manual snapshot** from the primary instance and confirm it
      appears in the RDS console with status `available`.
- [ ] **Perform a PITR restore** to a test instance using the procedure in
      section 1 above.  Target timestamp should be ≥ 5 minutes in the past.
- [ ] **Confirm data integrity** on the restored instance:
      - Run `python manage.py check --deploy` against the restored DB.
      - Verify row counts in key tables match the source.
- [ ] **Test cross-region restore** by listing replicated backups in `eu-west-2`
      and restoring one to a temporary instance in that region.
- [ ] **Delete all temporary test instances** created during testing.
- [ ] **Record the test date, results, and tester name** in the table below.

### Test Log

| Date | Tester | Test type | Outcome | Notes |
|------|--------|-----------|---------|-------|
| YYYY-MM-DD | Name | PITR / snapshot / cross-region | Pass / Fail | |

---

## Backup Monitoring & Alerting

AWS CloudWatch automatically emits the `FreeStorageSpace` and
`BackupRetentionPeriod` metrics for RDS.  Create a CloudWatch alarm on the metric
`RDS/BackupRetentionPeriod` to alert if it ever drops below 30 days.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "rds-backup-retention-check" \
  --metric-name "BackupRetentionPeriod" \
  --namespace "AWS/RDS" \
  --dimensions Name=DBInstanceIdentifier,Value=ai-error-explainer-db \
  --statistic Minimum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 30 \
  --comparison-operator LessThanThreshold \
  --alarm-actions <sns-topic-arn> \
  --region eu-west-1
```

---

## References

- [AWS RDS Automated Backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [AWS RDS Point-In-Time Recovery](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html)
- [Cross-Region Automated Backup Replication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html)
- Terraform resource: `aws_db_instance_automated_backups_replication`
