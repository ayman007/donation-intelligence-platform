data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project}-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
}

module "landing_bucket" {
  source = "../../modules/s3-bucket"

  name          = "${local.name_prefix}-landing-${local.account_id}"
  force_destroy = true
}

moved {
  from = aws_s3_bucket.landing
  to   = module.landing_bucket.aws_s3_bucket.this
}

moved {
  from = aws_s3_bucket_versioning.landing
  to   = module.landing_bucket.aws_s3_bucket_versioning.this
}

moved {
  from = aws_s3_bucket_server_side_encryption_configuration.landing
  to   = module.landing_bucket.aws_s3_bucket_server_side_encryption_configuration.this
}

moved {
  from = aws_s3_bucket_public_access_block.landing
  to   = module.landing_bucket.aws_s3_bucket_public_access_block.this
}

moved {
  from = aws_s3_bucket_lifecycle_configuration.landing
  to   = module.landing_bucket.aws_s3_bucket_lifecycle_configuration.this
}

module "raw_archive_bucket" {
  source = "../../modules/s3-bucket"

  name                               = "${local.name_prefix}-raw-archive-${local.account_id}"
  noncurrent_version_expiration_days = 90
  force_destroy                      = true
}
