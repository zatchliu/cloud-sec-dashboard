from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import IntEnum
from types import MappingProxyType
from typing import Any


class Severity(IntEnum):
    """The severity of a finding."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class Resource:
    identifier: str
    resource_type: str
    region: str
    config: Mapping[str, Any] = field(hash=False)

    def __post_init__(self) -> None:
        """Snapshot the config so later changes are not reflected."""
        frozen_config = MappingProxyType(self.config)
        object.__setattr__(self, "config", frozen_config)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    resource_id: str
    severity: Severity
    message: str
