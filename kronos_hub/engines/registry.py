from __future__ import annotations

from pathlib import Path
import os

from kronos_hub.engines.adapters.ai_hedge_fund import AiHedgeFundAdapter
from kronos_hub.engines.adapters.hybrid import HybridAdapter
from kronos_hub.engines.adapters.kronos import KronosAdapter
from kronos_hub.engines.adapters.tradingagents import TradingAgentsAdapter
from kronos_hub.shared.models import EngineDescriptor, HubHealth, RunRequest, RunResponse, SubprojectStatus
from kronos_hub.shared.project_paths import ProjectPaths


class EngineRegistry:
    def __init__(self, project_paths: ProjectPaths):
        self.project_paths = project_paths
        self._engines = {
            "ai_hedge_fund": AiHedgeFundAdapter(
                project_paths.ai_hedge_fund,
                python_executable=os.getenv("KRONOS_HUB_AI_HEDGE_FUND_PYTHON"),
            ),
            "tradingagents": TradingAgentsAdapter(
                project_paths.tradingagents,
                python_executable=os.getenv("KRONOS_HUB_TRADINGAGENTS_PYTHON"),
            ),
            "kronos": KronosAdapter(
                project_paths.kronos,
                python_executable=os.getenv("KRONOS_HUB_KRONOS_PYTHON"),
            ),
            "hybrid": HybridAdapter(),
        }

    @classmethod
    def from_env(cls, root_dir: Path | None = None) -> "EngineRegistry":
        return cls(ProjectPaths.discover(root_dir=root_dir))

    def list_engines(self) -> list[EngineDescriptor]:
        return [engine.describe() for engine in self._engines.values()]

    def get_engine(self, name: str):
        if name not in self._engines:
            raise KeyError(f"Unknown engine: {name}")
        return self._engines[name]

    def list_subprojects(self) -> list[SubprojectStatus]:
        results: list[SubprojectStatus] = []
        for key, path in self.project_paths.as_mapping().items():
            results.append(
                SubprojectStatus(
                    key=key,
                    path=str(path),
                    exists=path.exists(),
                    entrypoints=self.project_paths.entrypoints_for(key),
                    notes=["Discovered from workspace or environment variables."],
                )
            )
        return results

    def health(self) -> HubHealth:
        engines = self.list_engines()
        available_count = len([engine for engine in engines if engine.available])
        subprojects = self.list_subprojects()
        status = "ok" if available_count >= 3 else "degraded"
        return HubHealth(
            status=status,
            engine_count=len(engines),
            available_engine_count=available_count,
            subproject_count=len(subprojects),
        )

    def run(self, request: RunRequest) -> RunResponse:
        engine = self.get_engine(request.engine)
        return engine.run(request)
