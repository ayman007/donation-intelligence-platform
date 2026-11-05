# Donation Intelligence Platform

An end-to-end data platform built to learn and demonstrate the modern data stack:
Terraform, Kafka, Snowflake, dbt, Airflow, and an LLM/RAG layer.

**Status:** Phase 1 complete (Terraform + AWS foundation). Next: Phase 2, event simulator and data contracts.

## What's done so far

- Remote Terraform state in S3 with native locking
- Reusable S3 bucket module (versioning, encryption, no public access, lifecycle rules)
- Least-privilege IAM role, tested by proving what it cannot do
- Linting and formatting with tflint and pre-commit
- Documented rebuild process (see `infra/README.md`)

## Architecture

See [docs/architecture.md](docs/architecture.md) for the planned design, and
[docs/adr](docs/adr) for the decisions behind it.

## Stack

AWS (eu-north-1) · Terraform · Kafka · Snowflake · dbt · Airflow · LLM/RAG
