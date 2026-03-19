from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class LinkKind(StrEnum):
    MOCK = "mock"
    SERIAL = "serial"
    TCP = "tcp"
    BLUETOOTH = "bluetooth"


@dataclass(slots=True)
class SnapshotResult:
    label: str
    payload: dict[str, Any]
