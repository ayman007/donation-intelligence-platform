# ADR 0003: Use an IAM user with access keys for local development

## Status
Accepted (temporary)

## Context
The AWS free plan does not offer IAM Identity Center, which would give short-lived
credentials. Terraform and the CLI still need to authenticate from a laptop.

## Decision
Use a dedicated IAM user (no console access) with an access key stored only in the local
AWS credentials file. Pipelines use a separate least-privilege role (dev-pipeline).

## Consequences
Long-lived keys are a risk. Mitigations: MFA on the root user, keys never in the repo,
budget alerts, and deleting the key when the project ends. Revisit if the account moves
to a paid plan with Identity Center, or when CI is added (use OIDC then).
