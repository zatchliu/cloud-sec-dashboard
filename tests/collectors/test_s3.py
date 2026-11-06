import json
from unittest.mock import Mock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from app.collectors.s3 import collect_s3_buckets


def test_collect_s3_buckets_returns_bucket_resource_in_us_east_1() -> None:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="audit-logs")

        resources = collect_s3_buckets(client)

    assert len(resources) == 1
    resource = resources[0]
    assert resource.identifier == "arn:aws:s3:::audit-logs"
    assert resource.resource_type == "s3_bucket"
    assert resource.region == "us-east-1"


def test_collect_s3_buckets_includes_public_access_block_configuration() -> None:
    public_access_block = {
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True,
    }

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="audit-logs")
        client.put_public_access_block(
            Bucket="audit-logs",
            PublicAccessBlockConfiguration=public_access_block,
        )

        resources = collect_s3_buckets(client)

    assert resources[0].config["public_access_block"] == public_access_block


def test_collect_s3_buckets_uses_none_when_public_access_block_is_not_configured() -> (
    None
):
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="audit-logs")

        resources = collect_s3_buckets(client)

    assert resources[0].config["public_access_block"] is None


def test_collect_s3_buckets_includes_public_read_acl_grants() -> None:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="public-assets")
        client.put_bucket_acl(Bucket="public-assets", ACL="public-read")

        resources = collect_s3_buckets(client)

    grants = resources[0].config["acl"]
    assert any(
        grant["Grantee"].get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers"
        and grant["Permission"] == "READ"
        for grant in grants
    )


def test_collect_s3_buckets_includes_bucket_policy_as_a_parsed_dict() -> None:
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::audit-logs/*",
            }
        ],
    }

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="audit-logs")
        client.put_bucket_policy(Bucket="audit-logs", Policy=json.dumps(policy))

        resources = collect_s3_buckets(client)

    assert resources[0].config["policy"] == policy


def test_collect_s3_buckets_returns_all_buckets() -> None:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="audit-logs")
        client.create_bucket(Bucket="application-data")

        resources = collect_s3_buckets(client)

    assert {resource.identifier for resource in resources} == {
        "arn:aws:s3:::audit-logs",
        "arn:aws:s3:::application-data",
    }


def test_collect_s3_buckets_returns_bucket_region_outside_us_east_1() -> None:
    region = "us-west-2"

    with mock_aws():
        client = boto3.client("s3", region_name=region)
        client.create_bucket(
            Bucket="regional-audit-logs",
            CreateBucketConfiguration={"LocationConstraint": region},
        )

        resources = collect_s3_buckets(client)

    assert resources[0].region == region


def test_collect_s3_buckets_reraises_unexpected_public_access_block_errors() -> None:
    client = Mock()
    client.list_buckets.return_value = {"Buckets": [{"Name": "audit-logs"}]}
    client.get_bucket_location.return_value = {"LocationConstraint": None}
    client.get_public_access_block.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
        "GetPublicAccessBlock",
    )

    with pytest.raises(ClientError, match="AccessDenied"):
        collect_s3_buckets(client)
