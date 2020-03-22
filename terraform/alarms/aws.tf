provider "aws" {
  profile                 = var.profile
  shared_credentials_file = "~/.aws/credentials"
  region                  = "us-east-1"
  version                 = "~> 2.54.0"
}
