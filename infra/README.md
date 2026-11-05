# Infrastructure

Terraform code for the Donation Intelligence Platform. AWS region: eu-north-1.

## Layout

- `bootstrap/` creates the S3 bucket that stores Terraform state for everything else.
- `modules/s3-bucket/` is a reusable bucket module (versioning, encryption, no public access, lifecycle rules).
- `envs/dev/` is the dev environment: landing and raw-archive buckets, plus a least-privilege pipeline IAM role.

## Day-to-day workflow

    cd infra/envs/dev
    terraform fmt -recursive
    terraform validate
    terraform plan -out=tfplan
    terraform apply tfplan

## Rebuild from scratch (new AWS account)

1. In `bootstrap/`, temporarily move `backend.tf` aside, then run `terraform init` and `terraform apply`.
2. Put `backend.tf` back, update the bucket name in it (it contains the account ID), and run `terraform init -migrate-state`.
3. Update the bucket name in `envs/dev/backend.tf`, then run `terraform init` and `terraform apply` in `envs/dev/`.

## Teardown

Destroy `envs/dev` first. Never run `terraform destroy` in `bootstrap/` while other environments still use its bucket.

## Notes

- State locking uses the S3 backend's native lockfile (no DynamoDB). See `docs/adr/0002-s3-remote-state.md`.
- `force_destroy = true` is set on dev buckets only, because dev data is disposable.
