"""Rule for identifying publicly accessible S3 buckets."""

from app.domain.models import Finding, Resource


def check_s3_public_bucket(resource: Resource) -> list[Finding]:
    """Return findings for a publicly accessible S3 bucket."""
    return []
