data "aws_iam_policy_document" "landing_rw" {
  statement {
    sid       = "ReadWriteObjects"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${module.landing_bucket.arn}/*"]
  }

  statement {
    sid       = "ListBucket"
    actions   = ["s3:ListBucket"]
    resources = [module.landing_bucket.arn]
  }
}

data "aws_iam_policy_document" "pipeline_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.arn]
    }
  }
}

resource "aws_iam_policy" "landing_rw" {
  name        = "${local.name_prefix}-landing-rw"
  description = "Read and write objects in the landing bucket only."
  policy      = data.aws_iam_policy_document.landing_rw.json
}

resource "aws_iam_role" "pipeline" {
  name               = "${local.name_prefix}-pipeline"
  assume_role_policy = data.aws_iam_policy_document.pipeline_trust.json
}

resource "aws_iam_role_policy_attachment" "pipeline_landing_rw" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.landing_rw.arn
}
