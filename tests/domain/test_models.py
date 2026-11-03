from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import Finding, Resource, Severity


def test_severity_orders_risk_levels() -> None:
    """Rules can use severity thresholds, such as HIGH and above."""
    assert Severity.LOW < Severity.MEDIUM < Severity.HIGH < Severity.CRITICAL


def test_resource_preserves_its_collected_config() -> None:
    config = {"public_access_blocked": False, "versioning": "Enabled"}

    resource = Resource(
        identifier="arn:aws:s3:::audit-logs",
        resource_type="s3_bucket",
        region="us-east-1",
        config=config,
    )

    assert resource.identifier == "arn:aws:s3:::audit-logs"
    assert resource.resource_type == "s3_bucket"
    assert resource.region == "us-east-1"
    assert resource.config == config


def test_equal_resources_compare_equal() -> None:
    first = Resource(
        identifier="arn:aws:s3:::audit-logs",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_blocked": False},
    )
    second = Resource(
        identifier="arn:aws:s3:::audit-logs",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_blocked": False},
    )

    assert first == second


def test_resource_and_its_config_are_immutable() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::audit-logs",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_blocked": False},
    )

    with pytest.raises(FrozenInstanceError):
        resource.region = "eu-west-1"  # type: ignore[misc]

    with pytest.raises(TypeError):
        resource.config["public_access_blocked"] = True  # type: ignore[index]


def test_resource_is_hashable() -> None:
    resource = Resource(
        identifier="arn:aws:s3:::audit-logs",
        resource_type="s3_bucket",
        region="us-east-1",
        config={"public_access_blocked": False},
    )
    assert hash(resource) == hash(
        Resource(
            identifier="arn:aws:s3:::audit-logs",
            resource_type="s3_bucket",
            region="us-east-1",
            config={"public_access_blocked": False},
        )
    )


def test_finding_describes_a_rule_result() -> None:
    finding = Finding(
        rule_id="s3-public-access",
        resource_id="arn:aws:s3:::audit-logs",
        severity=Severity.HIGH,
        message="Bucket permits public access.",
    )

    assert finding.rule_id == "s3-public-access"
    assert finding.resource_id == "arn:aws:s3:::audit-logs"
    assert finding.severity is Severity.HIGH
    assert finding.message == "Bucket permits public access."


def test_equal_findings_compare_equal_and_are_immutable() -> None:
    first = Finding(
        rule_id="s3-public-access",
        resource_id="arn:aws:s3:::audit-logs",
        severity=Severity.HIGH,
        message="Bucket permits public access.",
    )
    second = Finding(
        rule_id="s3-public-access",
        resource_id="arn:aws:s3:::audit-logs",
        severity=Severity.HIGH,
        message="Bucket permits public access.",
    )

    assert first == second

    with pytest.raises(FrozenInstanceError):
        first.message = "Updated message."  # type: ignore[misc]
