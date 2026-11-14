import pytest

from app.domain.models import Resource, Severity
from app.rules.s3_public_bucket import check_s3_public_bucket


def test_public_acl_returns_high_severity_finding() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
        },
    )

    findings = check_s3_public_bucket(resource)

    assert len(findings) == 1
    assert findings[0].rule_id == "s3-public-access"
    assert findings[0].resource_id == "arn:aws:s3:::public-assets"
    assert findings[0].severity is Severity.HIGH
    assert findings[0].message == "Bucket permits public access through its ACL."


def test_public_allow_policy_returns_finding() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [],
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::public-assets/*",
                    }
                ],
            },
        },
    )

    findings = check_s3_public_bucket(resource)

    assert len(findings) == 1
    assert findings[0].rule_id == "s3-public-access"
    assert findings[0].resource_id == "arn:aws:s3:::public-assets"
    assert findings[0].severity is Severity.HIGH
    assert (
        findings[0].message == "Bucket permits public access through its bucket policy."
    )


def test_acl_and_policy_exposure_return_one_finding_for_bucket() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": {
                "Statement": {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::public-assets/*",
                }
            },
        },
    )

    findings = check_s3_public_bucket(resource)

    assert len(findings) == 1
    assert (
        findings[0].message
        == "Bucket permits public access through its ACL and bucket policy."
    )


def test_bucket_without_public_acl_or_policy_returns_no_findings() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::private-data",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_block": None, "acl": [], "policy": None},
    )

    assert check_s3_public_bucket(resource) == []


def test_missing_s3_config_keys_quietly_return_no_findings() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::incomplete-data",
        resource_type="s3_bucket",
        region="us-east-1",
        config={},
    )

    assert check_s3_public_bucket(resource) == []


def test_non_s3_resource_returns_no_findings() -> None:
    resource = Resource(
        identifier="arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
        resource_type="ec2_instance",
        region="us-east-1",
        config={},
    )

    assert check_s3_public_bucket(resource) == []


def test_authenticated_users_acl_grant_is_public() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": (
                            "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
                        ),
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
        },
    )

    assert len(check_s3_public_bucket(resource)) == 1


def test_public_acl_uri_on_non_group_grantee_is_not_public() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::private-data",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [
                {
                    "Grantee": {
                        "Type": "CanonicalUser",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
        },
    )

    assert check_s3_public_bucket(resource) == []


@pytest.mark.parametrize(
    ("setting", "expected_findings"),
    [("BlockPublicAcls", 1), ("IgnorePublicAcls", 0)],
)
def test_acl_block_setting_effect_on_existing_public_acl(
    setting: str, expected_findings: int
) -> None:
    public_access_block = {
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False,
    }
    public_access_block[setting] = True
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": public_access_block,
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
        },
    )

    assert len(check_s3_public_bucket(resource)) == expected_findings


@pytest.mark.parametrize(
    ("setting", "expected_findings"),
    [("BlockPublicPolicy", 1), ("RestrictPublicBuckets", 0)],
)
def test_policy_block_setting_effect_on_existing_public_policy(
    setting: str, expected_findings: int
) -> None:
    public_access_block = {
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False,
    }
    public_access_block[setting] = True
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": public_access_block,
            "acl": [],
            "policy": {
                "Statement": {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::public-assets/*",
                }
            },
        },
    )

    assert len(check_s3_public_bucket(resource)) == expected_findings


def test_acl_block_settings_do_not_neutralize_public_policy() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False,
            },
            "acl": [],
            "policy": {
                "Statement": {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::public-assets/*",
                }
            },
        },
    )

    assert len(check_s3_public_bucket(resource)) == 1


def test_policy_block_settings_do_not_neutralize_public_acl() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": {
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
        },
    )

    assert len(check_s3_public_bucket(resource)) == 1


def test_allow_policy_with_list_principal_containing_wildcard_is_public() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [],
            "policy": {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": ["arn:aws:iam::123456789012:root", "*"],
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::public-assets/*",
                    }
                ]
            },
        },
    )

    assert len(check_s3_public_bucket(resource)) == 1


def test_deny_policy_with_wildcard_principal_is_not_public() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::private-data",
        resource_type="s3_bucket",
        region="us-east-1",
        config={
            "public_access_block": None,
            "acl": [],
            "policy": {
                "Statement": [
                    {
                        "Effect": "Deny",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::private-data/*",
                    }
                ]
            },
        },
    )

    assert check_s3_public_bucket(resource) == []


@pytest.mark.parametrize(
    "config",
    [
        {"acl": "not-a-list", "policy": None, "public_access_block": None},
        {"acl": [], "policy": "not-a-mapping", "public_access_block": None},
        {
            "acl": [
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                }
            ],
            "policy": None,
            "public_access_block": "not-a-mapping",
        },
    ],
)
def test_malformed_top_level_config_values_raise_type_error(
    config: dict[str, object],
) -> None:
    resource = Resource(
        identifier="arn:aws:s3:::public-assets",
        resource_type="s3_bucket",
        region="us-east-1",
        config=config,
    )

    with pytest.raises(TypeError):
        check_s3_public_bucket(resource)
