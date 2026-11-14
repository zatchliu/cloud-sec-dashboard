"""Rule for identifying publicly accessible S3 buckets."""

from collections.abc import Mapping
from typing import Any

from app.domain.models import Finding, Resource, Severity

_PUBLIC_ACL_URIS = frozenset(
    {
        "http://acs.amazonaws.com/groups/global/AllUsers",
        "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
    }
)


def check_s3_public_bucket(resource: Resource) -> list[Finding]:
    """Return findings for a publicly accessible S3 bucket."""
    if resource.resource_type != "s3_bucket":
        return []

    public_access_block = resource.config.get("public_access_block")
    acl_is_public = _acl_is_public(resource.config.get("acl", []))
    policy_is_public = _policy_is_public(resource.config.get("policy"))
    acl_is_exposed = acl_is_public and not _acl_is_blocked(public_access_block)
    policy_is_exposed = policy_is_public and not _policy_is_blocked(public_access_block)

    if not acl_is_exposed and not policy_is_exposed:
        return []

    access_paths = []
    if acl_is_exposed:
        access_paths.append("ACL")
    if policy_is_exposed:
        access_paths.append("bucket policy")
    message = f"Bucket permits public access through its {' and '.join(access_paths)}."

    return [
        Finding(
            rule_id="s3-public-access",
            resource_id=resource.identifier,
            severity=Severity.HIGH,
            message=message,
        )
    ]


def _acl_is_public(grants: Any) -> bool:
    """Return whether any ACL grant targets a global S3 group."""
    if not isinstance(grants, list):
        raise TypeError("S3 ACL grants must be a list")

    for grant in grants:
        if not isinstance(grant, Mapping):
            raise TypeError("Each S3 ACL grant must be a mapping")

        grantee = grant.get("Grantee")
        if not isinstance(grantee, Mapping):
            raise TypeError("Each S3 ACL grant must contain a grantee mapping")

        uri = grantee.get("URI")
        if (
            grantee.get("Type") == "Group"
            and isinstance(uri, str)
            and uri in _PUBLIC_ACL_URIS
        ):
            return True

    return False


def _policy_is_public(policy: Any) -> bool:
    """Return whether an Allow statement grants access to every principal."""
    if policy is None:
        return False
    if not isinstance(policy, Mapping):
        raise TypeError("S3 bucket policy must be a mapping or None")

    statements = policy.get("Statement", [])
    if isinstance(statements, Mapping):
        statements = [statements]
    if not isinstance(statements, list):
        raise TypeError("S3 bucket policy Statement must be a mapping or list")

    for statement in statements:
        if not isinstance(statement, Mapping):
            raise TypeError("Each S3 bucket policy statement must be a mapping")
        if statement.get("Effect") == "Allow" and _principal_is_public(
            statement.get("Principal")
        ):
            return True

    return False


def _principal_is_public(principal: Any) -> bool:
    """Return whether a policy principal includes the public wildcard."""
    if principal == "*":
        return True
    if isinstance(principal, Mapping):
        aws_principal = principal.get("AWS")
        return aws_principal == "*" or (
            isinstance(aws_principal, list) and "*" in aws_principal
        )
    if isinstance(principal, list):
        return any(_principal_is_public(item) for item in principal)
    if principal is not None and not isinstance(principal, str):
        raise TypeError("S3 bucket policy Principal must be a string, mapping, or list")
    return False


def _acl_is_blocked(public_access_block: Any) -> bool:
    """Return whether public ACL grants are neutralized by bucket settings."""
    if public_access_block is None:
        return False
    if not isinstance(public_access_block, Mapping):
        raise TypeError(
            "S3 public access block configuration must be a mapping or None"
        )
    return _setting_is_enabled(public_access_block, "IgnorePublicAcls")


def _policy_is_blocked(public_access_block: Any) -> bool:
    """Return whether public policy access is neutralized by bucket settings."""
    if public_access_block is None:
        return False
    if not isinstance(public_access_block, Mapping):
        raise TypeError(
            "S3 public access block configuration must be a mapping or None"
        )
    return _setting_is_enabled(public_access_block, "RestrictPublicBuckets")


def _setting_is_enabled(public_access_block: Mapping[str, Any], setting: str) -> bool:
    value = public_access_block.get(setting, False)
    if not isinstance(value, bool):
        raise TypeError(f"S3 public access block setting {setting} must be a boolean")
    return value
