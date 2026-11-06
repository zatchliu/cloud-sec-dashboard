from __future__ import annotations

from typing import Any

from botocore.exceptions import ClientError

from app.domain.models import Resource


def collect_s3_buckets(client: Any) -> list[Resource]:
    """Translate buckets visible to ``client`` into domain resources.

    Each resource has one collector-owned configuration key:
    ``public_access_block``, containing S3's four boolean settings or ``None``
    when the bucket has no public-access-block configuration.
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
                    "public_access_block": _get_public_access_block(client, bucket_name)
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
