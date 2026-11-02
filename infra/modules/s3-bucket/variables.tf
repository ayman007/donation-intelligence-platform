variable "name" {
  description = "Globally unique bucket name."
  type        = string
}

variable "force_destroy" {
  description = "Allow Terraform to delete the bucket even if it contains objects."
  type        = bool
  default     = false
}

variable "noncurrent_version_expiration_days" {
  description = "Days before old object versions are deleted."
  type        = number
  default     = 30
}

variable "abort_incomplete_upload_days" {
  description = "Days before incomplete multipart uploads are aborted."
  type        = number
  default     = 7
}
