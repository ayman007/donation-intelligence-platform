output "account_id" {
  description = "AWS account this environment is deployed to."
  value       = data.aws_caller_identity.current.account_id
}
