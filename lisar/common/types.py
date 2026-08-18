from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Point = tuple[int, int]
BBox = tuple[int, int, int, int]


@dataclass
class TargetDetection:
    center: Point
    bbox: BBox | None
    confidence: float
    source: str
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass
class LaserReferencePoint:
    center: Point
    predicted: bool
    source: str
    debug: dict[str, Any] = field(default_factory=dict)

