# Northwind Tech — Backup and Disaster Recovery Policy (v1.8)

## 1. Backups

### BR-1.1 Backup schedule

Production databases are backed up with daily incremental backups and weekly full backups.

### BR-1.2 Backup protection

Backups are encrypted with AES-256 and stored in a separate cloud account with restricted access. Only two named infrastructure roles can access the backup account.

### BR-1.3 Restore testing

Restore tests are performed every quarter and the results are documented.

## 2. Disaster recovery

### BR-2.1 Recovery objectives

For production systems the recovery time objective (RTO) is 8 hours and the recovery point objective (RPO) is 24 hours.

### BR-2.2 Ransomware resilience

Backups are immutable for 35 days: they cannot be modified or deleted during that period, even by administrators. The disaster recovery plan is tested once a year.

## 3. Legacy notes

### BR-3.1 Customer data retention in backups

Customer data is retained for 90 days after contract end to allow for recovery requests, after which it is permanently deleted.
