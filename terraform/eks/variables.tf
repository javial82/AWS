variable "vpc" {
  default = ""
}

variable "pub_subnets" {
  type    = "list"
  default = []
}

variable "priv_subnets" {
  type    = "list"
  default = []
}

variable "profile" {
  default = "dev"
}
