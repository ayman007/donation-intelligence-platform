variable "project" {
  description = "Short project prefix used in resource names."
  type        = string
  default     = "dip"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region."
  type        = string
  default     = "eu-north-1"
}
