from __future__ import annotations

from kronos_hub.engines.base import BaseEngineAdapter
from kronos_hub.shared.contracts import ExecutionMode, RunStatus
from kronos_hub.shared.models import RunRequest, RunResponse
from kronos_hub.shared.worker_client import WorkerExecutionError
from kronos_hub.services.ai_hedge_fund import AiHedgeFundService


class AiHedgeFundAdapter(BaseEngineAdapter):
    name = "ai_hedge_fund"
    display_name = "AI Hedge Fund"
    description = "Existing multi-agent hedge fund app with CLI, backtester, backend, and frontend."
    capabilities = (
        "cli_execution",
        "backtesting",
        "fastapi_backend",
        "frontend_shell",
    )

    def __init__(self, project_root, python_executable: str | None = None):
        super().__init__(project_root)
        self.service = AiHedgeFundService(str(self.project_root), python_executable=python_executable)

    def build_command(self, request: RunRequest) -> str:
        tickers = ",".join(request.tickers) if request.tickers else "AAPL"
        command = f"python src/main.py --ticker {tickers}"
        if request.start_date:
            command += f" --start-date {request.start_date.isoformat()}"
        if request.end_date:
            command += f" --end-date {request.end_date.isoformat()}"
        return command

    def run(self, request: RunRequest) -> RunResponse:
        if not self.is_available():
            return self.not_available_response(
                "AI Hedge Fund project directory was not found.",
                next_steps=[
                    "Verify KRONOS_HUB_AI_HEDGE_FUND_PATH.",
                    "Confirm ai-hedge-fund-main is present under the workspace.",
                ],
            )

        command = self.build_command(request)
        if request.dry_run:
            return self.planned_response(
                "AI Hedge Fund adapter is registered. Runtime handoff is not wired yet, but the execution contract is in place.",
                metadata={
                    "suggested_command": command,
                    "backend_entrypoint": "app/backend/main.py",
                    "api_mode": "Can later be proxied behind the hub gateway.",
                },
                next_steps=[
                    "Wrap src.main.run_hedge_fund in a stable service function.",
                    "Expose backtest and live analysis through the hub gateway.",
                    "Optionally reuse the existing frontend as a downstream UI module.",
                ],
                execution_mode=ExecutionMode.HANDOFF,
                status=RunStatus.STUB,
            )

        try:
            options = request.options or {}
            if options.get("mode") == "backtest":
                if not request.start_date or not request.end_date:
                    return self.failed_response(
                        "AI Hedge Fund backtest requires start_date and end_date.",
                        next_steps=["Provide start_date and end_date for backtest mode."],
                    )
                result = self.service.run_backtest(
                    tickers=request.tickers,
                    start_date=request.start_date.isoformat(),
                    end_date=request.end_date.isoformat(),
                    initial_capital=float(options.get("initial_capital", 100000.0)),
                    margin_requirement=float(options.get("margin_requirement", 0.0)),
                    selected_analysts=options.get("selected_analysts"),
                    model_name=options.get("model_name", "gpt-4.1"),
                    model_provider=options.get("model_provider", "OpenAI"),
                    api_keys=request.api_keys,
                    environment=request.environment,
                )
                return self.completed_response(
                    "AI Hedge Fund backtest completed through the hub worker runtime.",
                    result=result,
                    metadata={"worker_mode": "subprocess", "suggested_command": command},
                )

            if not request.start_date or not request.end_date:
                return self.failed_response(
                    "AI Hedge Fund execution requires start_date and end_date.",
                    next_steps=["Provide start_date and end_date for run mode."],
                )

            result = self.service.run_analysis(
                tickers=request.tickers,
                start_date=request.start_date.isoformat(),
                end_date=request.end_date.isoformat(),
                initial_cash=float(options.get("initial_cash", 100000.0)),
                margin_requirement=float(options.get("margin_requirement", 0.0)),
                selected_analysts=options.get("selected_analysts"),
                model_name=options.get("model_name", "gpt-4.1"),
                model_provider=options.get("model_provider", "OpenAI"),
                show_reasoning=bool(options.get("show_reasoning", False)),
                portfolio_positions=options.get("portfolio_positions"),
                api_keys=request.api_keys,
                environment=request.environment,
            )
            return self.completed_response(
                "AI Hedge Fund execution completed through the hub worker runtime.",
                result=result,
                metadata={"worker_mode": "subprocess", "suggested_command": command},
            )
        except WorkerExecutionError as exc:
            return self.failed_response(
                "AI Hedge Fund worker execution failed.",
                metadata={"stdout": exc.stdout, "stderr": exc.stderr},
                next_steps=[
                    "Check KRONOS_HUB_AI_HEDGE_FUND_PYTHON points at an environment with ai-hedge-fund dependencies installed.",
                    "Verify required API keys are available for the selected model provider and market data provider.",
                ],
            )
