from __future__ import annotations

import json
from typing import Any

from botocore.exceptions import ClientError

from app.domain.models import Resource


def collect_s3_buckets(client: Any) -> list[Resource]:
    """Translate buckets visible to ``client`` into domain resources.

    Each resource includes the bucket's public-access-block settings, ACL
    grants, and parsed policy in its configuration.
    """
    resources: list[Resource] = []

    for bucket in client.list_buckets()["Buckets"]:
        bucket_name = bucket["Name"]
        location = client.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
        region = "us-east-1" if location is None else location

        resources.append(
            Resource(
                identifier=f"arn:aws:s3:::{bucket_name}",
                resource_type="s3_bucket",
                region=region,
                config={
                    "public_access_block": _get_public_access_block(
                        client, bucket_name
                    ),
                    "acl": client.get_bucket_acl(Bucket=bucket_name)["Grants"],
                    "policy": _get_bucket_policy(client, bucket_name),
                },
            )
        )

    return resources


def _get_public_access_block(client: Any, bucket_name: str) -> dict[str, bool] | None:
    """Return a bucket's public-access block, or None when it is absent."""
    try:
        response = client.get_public_access_block(Bucket=bucket_name)
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            return None
        raise

    return response["PublicAccessBlockConfiguration"]


def _get_bucket_policy(client: Any, bucket_name: str) -> dict[str, Any] | None:
    """Return a bucket policy as a dictionary, or None when it is absent."""
    try:
        response = client.get_bucket_policy(Bucket=bucket_name)
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return None
        raise

    return json.loads(response["Policy"])
