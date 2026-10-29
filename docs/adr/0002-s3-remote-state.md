# ADR 0002: Store Terraform state in S3 with native locking

## Status
Accepted

## Context
Terraform keeps a state file mapping code to real resources. A local file is easy to
lose and cannot be shared safely.

## Decision
Keep state in a versioned, encrypted, private S3 bucket (created by a small bootstrap
config) and use the S3 backend's native lockfile (use_lockfile) instead of DynamoDB,
which is deprecated for locking.

## Consequences
State is recoverable (versioning), protected (encryption, no public access), and
locked during applies. The bootstrap config itself starts with local state.
