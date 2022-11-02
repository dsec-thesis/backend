resource "aws_s3_bucket" "tf_state" {
  bucket = "${var.project}-state"

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "tf_state" {
  hash_key     = "LockID"
  name         = "${var.project}-locks"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "LockID"
    type = "S"

  }
}
