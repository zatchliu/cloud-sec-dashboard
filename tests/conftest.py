"""Shared pytest configuration."""

import pytest


@pytest.fixture(autouse=True)
def fake_aws_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent tests from loading credentials or profiles from the host."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing-secret-key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing-session-token")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")

    for variable in (
        "AWS_PROFILE",
        "AWS_DEFAULT_PROFILE",
        "AWS_CONFIG_FILE",
        "AWS_SHARED_CREDENTIALS_FILE",
    ):
        monkeypatch.delenv(variable, raising=False)
