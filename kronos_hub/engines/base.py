from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from kronos_hub.shared.contracts import ExecutionMode, RunStatus
from kronos_hub.shared.models import EngineDescriptor, PipelineStage, RunRequest, RunResponse


class BaseEngineAdapter(ABC):
    name: str = ""
    display_name: str = ""
    description: str = ""
    capabilities: tuple[str, ...] = ()

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root.resolve() if project_root else None

    def is_available(self) -> bool:
        if self.project_root is None:
            return True
        return self.project_root.exists()

    def describe(self) -> EngineDescriptor:
        return EngineDescriptor(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            capabilities=list(self.capabilities),
            project_root=str(self.project_root) if self.project_root else None,
            available=self.is_available(),
            notes=self.notes(),
        )

    def notes(self) -> list[str]:
        if self.is_available():
            return ["Subproject path discovered."]
        return ["Subproject path is missing."]

    def not_available_response(self, message: str, next_steps: list[str] | None = None) -> RunResponse:
        return RunResponse(
            engine=self.name,
            status=RunStatus.UNAVAILABLE.value,
            message=message,
            project_root=str(self.project_root) if self.project_root else None,
            execution_mode=ExecutionMode.ADAPTER.value,
            capabilities=list(self.capabilities),
            next_steps=next_steps or [],
        )

    def planned_response(
        self,
        message: str,
        *,
        result: dict | None = None,
        metadata: dict | None = None,
        next_steps: list[str] | None = None,
        execution_mode: ExecutionMode = ExecutionMode.HANDOFF,
        pipeline: list[PipelineStage] | None = None,
        status: RunStatus = RunStatus.STUB,
    ) -> RunResponse:
        return RunResponse(
            engine=self.name,
            status=status.value,
            message=message,
            project_root=str(self.project_root) if self.project_root else None,
            execution_mode=execution_mode.value,
            capabilities=list(self.capabilities),
            next_steps=next_steps or [],
            result=result or {},
            metadata=metadata or {},
            pipeline=pipeline or [],
        )

    def completed_response(
        self,
        message: str,
        *,
        result: dict | None = None,
        metadata: dict | None = None,
        next_steps: list[str] | None = None,
        execution_mode: ExecutionMode = ExecutionMode.ADAPTER,
    ) -> RunResponse:
        return RunResponse(
            engine=self.name,
            status=RunStatus.COMPLETED.value,
            message=message,
            project_root=str(self.project_root) if self.project_root else None,
            execution_mode=execution_mode.value,
            capabilities=list(self.capabilities),
            next_steps=next_steps or [],
            result=result or {},
            metadata=metadata or {},
        )

    def failed_response(
        self,
        message: str,
        *,
        metadata: dict | None = None,
        next_steps: list[str] | None = None,
    ) -> RunResponse:
        return RunResponse(
            engine=self.name,
            status=RunStatus.FAILED.value,
            message=message,
            project_root=str(self.project_root) if self.project_root else None,
            execution_mode=ExecutionMode.ADAPTER.value,
            capabilities=list(self.capabilities),
            next_steps=next_steps or [],
            metadata=metadata or {},
        )

    @abstractmethod
    def run(self, request: RunRequest) -> RunResponse:
        raise NotImplementedError
