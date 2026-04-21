from __future__ import annotations

from kronos_hub.engines.base import BaseEngineAdapter
from kronos_hub.shared.contracts import ExecutionMode, RunStatus
from kronos_hub.shared.models import RunRequest, RunResponse
from kronos_hub.shared.worker_client import WorkerExecutionError
from kronos_hub.services.trading_research import TradingResearchService


class TradingAgentsAdapter(BaseEngineAdapter):
    name = "tradingagents"
    display_name = "TradingAgents"
    description = "Multi-agent trading research framework with graph orchestration and configurable data vendors."
    capabilities = (
        "research_debate",
        "graph_orchestration",
        "vendor_routing",
        "cli_execution",
    )

    def __init__(self, project_root, python_executable: str | None = None):
        super().__init__(project_root)
        self.service = TradingResearchService(str(self.project_root), python_executable=python_executable)

    def build_command(self, request: RunRequest) -> str:
        ticker = request.tickers[0] if request.tickers else "NVDA"
        trade_date = request.trade_date or request.end_date
        date_value = trade_date.isoformat() if trade_date else "2026-01-15"
        return (
            "python -c \"from tradingagents.graph.trading_graph import TradingAgentsGraph; "
            "from tradingagents.default_config import DEFAULT_CONFIG; "
            f"ta=TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy()); "
            f"_, decision = ta.propagate('{ticker}', '{date_value}'); print(decision)\""
        )

    def run(self, request: RunRequest) -> RunResponse:
        if not self.is_available():
            return self.not_available_response(
                "TradingAgents project directory was not found.",
                next_steps=[
                    "Verify KRONOS_HUB_TRADINGAGENTS_PATH.",
                    "Confirm TradingAgents-main exists in the workspace.",
                ],
            )

        command = self.build_command(request)
        if request.dry_run:
            return self.planned_response(
                "TradingAgents adapter is registered. The hub can already describe and target this engine; direct invocation is the next wiring step.",
                metadata={
                    "suggested_command": command,
                    "engine_class": "tradingagents.graph.trading_graph.TradingAgentsGraph",
                    "integration_note": "This project is the best candidate for the shared research engine core.",
                },
                next_steps=[
                    "Wrap TradingAgentsGraph.propagate in a stable adapter service.",
                    "Normalize final decision output into a shared signal schema.",
                    "Add optional forecast injection points for Kronos outputs.",
                ],
                execution_mode=ExecutionMode.HANDOFF,
                status=RunStatus.STUB,
            )

        try:
            options = request.options or {}
            ticker = request.tickers[0] if request.tickers else options.get("ticker")
            trade_date = request.trade_date or request.end_date
            if not ticker or not trade_date:
                return self.failed_response(
                    "TradingAgents requires a ticker and trade_date/end_date.",
                    next_steps=["Provide request.tickers[0] and request.trade_date (or end_date)."],
                )
            result = self.service.run(
                ticker=ticker,
                trade_date=trade_date.isoformat(),
                selected_analysts=options.get("selected_analysts"),
                llm_provider=options.get("llm_provider"),
                deep_think_llm=options.get("deep_think_llm"),
                quick_think_llm=options.get("quick_think_llm"),
                max_debate_rounds=options.get("max_debate_rounds"),
                max_risk_discuss_rounds=options.get("max_risk_discuss_rounds"),
                output_language=options.get("output_language"),
                backend_url=options.get("backend_url"),
                data_vendors=options.get("data_vendors"),
                tool_vendors=options.get("tool_vendors"),
                debug=bool(options.get("debug", False)),
                config_overrides=options.get("config_overrides"),
                api_keys=request.api_keys,
                environment=request.environment,
            )
            return self.completed_response(
                "TradingAgents research completed through the hub worker runtime.",
                result=result,
                metadata={"worker_mode": "subprocess", "suggested_command": command},
            )
        except WorkerExecutionError as exc:
            return self.failed_response(
                "TradingAgents worker execution failed.",
                metadata={"stdout": exc.stdout, "stderr": exc.stderr},
                next_steps=[
                    "Check KRONOS_HUB_TRADINGAGENTS_PYTHON points at an environment with TradingAgents dependencies installed.",
                    "Verify required API keys are available for the selected LLM provider.",
                ],
            )
