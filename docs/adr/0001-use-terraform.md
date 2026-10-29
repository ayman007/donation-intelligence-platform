# ADR 0001: Use Terraform for infrastructure

## Status
Accepted

## Context
All cloud and warehouse infrastructure should be reproducible, reviewable, and
rebuildable from code rather than created by hand in consoles.

## Decision
Use Terraform for AWS and Snowflake resources, with remote state in S3.

## Consequences
Every resource lives in version control. Rebuilding an environment is one command.
It also means learning state management and module design up front.
