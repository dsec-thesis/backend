terraform {
  required_version = ">= 1.2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.16"
    }
  }

  backend "s3" {
    bucket         = "parking-state"
    dynamodb_table = "parking-locks"
    key            = "tf/state.tfstate"
    region         = "us-east-1"
    profile        = "parking-dev"
  }
}


provider "aws" {
  region  = var.region
  # profile = "${var.project}"


  default_tags {
    tags = {
      Project = var.project
      Env     = terraform.workspace
    }
  }
}
