provider "aws" {
  profile                 = var.profile
  shared_credentials_file = "~/.aws/credentials"
  region                  = "eu-central-1"
  version                 = "~> 2.13"
}
