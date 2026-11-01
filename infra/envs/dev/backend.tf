terraform {
  backend "s3" {
    bucket       = "dip-tfstate-113732354136"
    key          = "dev/terraform.tfstate"
    region       = "eu-north-1"
    use_lockfile = true
    encrypt      = true
  }
}
