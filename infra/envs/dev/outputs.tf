output "account_id" {
  description = "AWS account this environment is deployed to."
  value       = data.aws_caller_identity.current.account_id
}

output "landing_bucket_name" {
  description = "Name of the landing bucket."
  value       = aws_s3_bucket.landing.id
}

output "landing_bucket_arn" {
  description = "ARN of the landing bucket."
  value       = aws_s3_bucket.landing.arn
}
