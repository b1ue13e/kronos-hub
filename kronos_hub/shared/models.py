from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass(slots=True)
class EngineDescriptor:
    name: str
    display_name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    project_root: str | None = None
    available: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SubprojectStatus:
    key: str
    path: str
    exists: bool
    entrypoints: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PipelineStage:
    name: str
    description: str
    engine: str | None = None
    output_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunRequest:
    engine: str
    tickers: list[str] = field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    trade_date: date | None = None
    dry_run: bool = True
    api_keys: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunResponse:
    engine: str
    status: str
    message: str
    project_root: str | None = None
    execution_mode: str = "adapter"
    capabilities: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    pipeline: list[PipelineStage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["pipeline"] = [stage.to_dict() for stage in self.pipeline]
        return payload


@dataclass(slots=True)
class HubHealth:
    status: str
    engine_count: int
    available_engine_count: int
    subproject_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
