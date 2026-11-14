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


def test_bucket_without_public_acl_or_policy_returns_no_findings() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::private-data",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_block": None, "acl": [], "policy": None},
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
