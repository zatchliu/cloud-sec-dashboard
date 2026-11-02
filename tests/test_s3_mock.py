"""Examples of AWS interactions tested without an AWS account."""

import boto3
from moto import mock_aws


def test_create_and_list_s3_bucket() -> None:
    """Moto stores the created bucket in an in-memory fake S3 service."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-cloud-sec-dashboard")

        response = s3.list_buckets()

    assert [bucket["Name"] for bucket in response["Buckets"]] == [
        "test-cloud-sec-dashboard"
    ]
