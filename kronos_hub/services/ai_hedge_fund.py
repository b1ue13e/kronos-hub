from __future__ import annotations

from typing import Any

from kronos_hub.shared.worker_client import get_python_executable, run_json_worker


class AiHedgeFundService:
    def __init__(self, project_root: str, python_executable: str | None = None):
        self.project_root = project_root
        self.python_executable = python_executable or get_python_executable("KRONOS_HUB_AI_HEDGE_FUND_PYTHON")

    def run_analysis(
        self,
        *,
        tickers: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
        initial_cash: float = 100000.0,
        margin_requirement: float = 0.0,
        selected_analysts: list[str] | None = None,
        model_name: str = "gpt-4.1",
        model_provider: str = "OpenAI",
        show_reasoning: bool = False,
        portfolio_positions: list[dict[str, Any]] | None = None,
        api_keys: dict[str, str] | None = None,
        environment: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "command": "run",
            "project_root": self.project_root,
            "tickers": tickers,
            "start_date": start_date,
            "end_date": end_date,
            "initial_cash": initial_cash,
            "margin_requirement": margin_requirement,
            "selected_analysts": selected_analysts or [],
            "model_name": model_name,
            "model_provider": model_provider,
            "show_reasoning": show_reasoning,
            "portfolio_positions": portfolio_positions or [],
        }
        merged_env = {}
        merged_env.update(environment or {})
        merged_env.update(api_keys or {})
        return run_json_worker(
            worker_script_name="ai_hedge_fund_worker.py",
            payload=payload,
            python_executable=self.python_executable,
            env_overrides=merged_env,
        )

    def run_backtest(
        self,
        *,
        tickers: list[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0,
        margin_requirement: float = 0.0,
        selected_analysts: list[str] | None = None,
        model_name: str = "gpt-4.1",
        model_provider: str = "OpenAI",
        portfolio_positions: list[dict[str, Any]] | None = None,
        api_keys: dict[str, str] | None = None,
        environment: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "command": "backtest",
            "project_root": self.project_root,
            "tickers": tickers,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "margin_requirement": margin_requirement,
            "selected_analysts": selected_analysts or [],
            "model_name": model_name,
            "model_provider": model_provider,
            "portfolio_positions": portfolio_positions or [],
        }
        merged_env = {}
        merged_env.update(environment or {})
        merged_env.update(api_keys or {})
        return run_json_worker(
            worker_script_name="ai_hedge_fund_worker.py",
            payload=payload,
            python_executable=self.python_executable,
            env_overrides=merged_env,
        )
