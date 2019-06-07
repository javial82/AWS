resource "aws_eks_cluster" "xavi_cluster" {
  name     = "xavieks"
  role_arn = "${aws_iam_role.xavi_cluster_role.arn}"

  vpc_config {
    subnet_ids = ["${data.aws_subnet_ids.test.ids}"]
  }
}

resource "aws_iam_role" "xavi_cluster_role" {
  name = "xavi-cluster-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "xavi-cluster-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = "${ aws_iam_role.xavi_cluster_role.name }"
}

resource "aws_iam_role_policy_attachment" "cluster-AmazonEKSServicePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = "${ aws_iam_role.xavi_cluster_role.name }"
}

resource "aws_vpc" "xavi_vpc" {
  cidr_block = "${var.vpc}"
}

resource "aws_subnet" "xavi_pub_subnets" {
  count      = "${ length(var.pub_subnets) }"
  vpc_id     = "${ aws_vpc.xavi_vpc.id }"
  cidr_block = "${ var.pub_subnets[count.index] }"

  tags = {
    Name = "xavi_public"
  }
}

resource "aws_subnet" "xavi_priv_subnets" {
  count      = "${ length(var.priv_subnets) }"
  vpc_id     = "${ aws_vpc.xavi_vpc.id }"
  cidr_block = "${ var.priv_subnets[count.index] }"

  tags = {
    Name = "xavi_public"
  }
}

data "aws_subnet_ids" "test" {
  vpc_id = "${aws_vpc.xavi_vpc.id}"
}

#data "aws_subnet" "test2" {
#  count = "${length(data.aws_subnet_ids.test.ids)}"
#  id    = "${data.aws_subnet_ids.test.ids[count.index]}"
#}
