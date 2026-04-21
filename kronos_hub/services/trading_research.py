from __future__ import annotations

from typing import Any

from kronos_hub.shared.worker_client import get_python_executable, run_json_worker


class TradingResearchService:
    def __init__(self, project_root: str, python_executable: str | None = None):
        self.project_root = project_root
        self.python_executable = python_executable or get_python_executable("KRONOS_HUB_TRADINGAGENTS_PYTHON")

    def run(
        self,
        *,
        ticker: str,
        trade_date: str,
        selected_analysts: list[str] | None = None,
        llm_provider: str | None = None,
        deep_think_llm: str | None = None,
        quick_think_llm: str | None = None,
        max_debate_rounds: int | None = None,
        max_risk_discuss_rounds: int | None = None,
        output_language: str | None = None,
        backend_url: str | None = None,
        data_vendors: dict[str, str] | None = None,
        tool_vendors: dict[str, str] | None = None,
        debug: bool = False,
        config_overrides: dict[str, Any] | None = None,
        api_keys: dict[str, str] | None = None,
        environment: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "command": "research",
            "project_root": self.project_root,
            "ticker": ticker,
            "trade_date": trade_date,
            "selected_analysts": selected_analysts or ["market", "social", "news", "fundamentals"],
            "debug": debug,
            "config_overrides": config_overrides or {},
        }
        if llm_provider is not None:
            payload["config_overrides"]["llm_provider"] = llm_provider
        if deep_think_llm is not None:
            payload["config_overrides"]["deep_think_llm"] = deep_think_llm
        if quick_think_llm is not None:
            payload["config_overrides"]["quick_think_llm"] = quick_think_llm
        if max_debate_rounds is not None:
            payload["config_overrides"]["max_debate_rounds"] = max_debate_rounds
        if max_risk_discuss_rounds is not None:
            payload["config_overrides"]["max_risk_discuss_rounds"] = max_risk_discuss_rounds
        if output_language is not None:
            payload["config_overrides"]["output_language"] = output_language
        if backend_url is not None:
            payload["config_overrides"]["backend_url"] = backend_url
        if data_vendors is not None:
            payload["config_overrides"]["data_vendors"] = data_vendors
        if tool_vendors is not None:
            payload["config_overrides"]["tool_vendors"] = tool_vendors

        merged_env = {}
        merged_env.update(environment or {})
        merged_env.update(api_keys or {})

        return run_json_worker(
            worker_script_name="tradingagents_worker.py",
            payload=payload,
            python_executable=self.python_executable,
            env_overrides=merged_env,
        )
