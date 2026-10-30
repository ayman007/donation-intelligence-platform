variable "project" {
  description = "Short project prefix used in resource names."
  type        = string
  default     = "dip"
}

variable "region" {
  description = "AWS region for the state bucket."
  type        = string
  default     = "eu-north-1"
}
