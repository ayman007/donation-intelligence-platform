output "account_id" {
  description = "AWS account this environment is deployed to."
  value       = data.aws_caller_identity.current.account_id
}

output "landing_bucket_name" {
  description = "Name of the landing bucket."
  value       = module.landing_bucket.id
}

output "landing_bucket_arn" {
  description = "ARN of the landing bucket."
  value       = module.landing_bucket.arn
}

output "raw_archive_bucket_name" {
  description = "Name of the raw archive bucket."
  value       = module.raw_archive_bucket.id
}
