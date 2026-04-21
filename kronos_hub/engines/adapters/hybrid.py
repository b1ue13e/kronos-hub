from __future__ import annotations

from kronos_hub.engines.base import BaseEngineAdapter
from kronos_hub.shared.contracts import ExecutionMode, RunStatus
from kronos_hub.shared.models import PipelineStage, RunRequest, RunResponse


class HybridAdapter(BaseEngineAdapter):
    name = "hybrid"
    display_name = "Hybrid Pipeline"
    description = "Planned orchestration mode that chains Kronos, TradingAgents, and AI Hedge Fund under one contract."
    capabilities = (
        "forecast_plus_research",
        "multi_engine_orchestration",
        "shared_signal_contract",
    )

    def run(self, request: RunRequest) -> RunResponse:
        pipeline = [
            PipelineStage(
                name="forecast",
                description="Generate forecast context from Kronos.",
                engine="kronos",
                output_hint="OHLCV forecast, derived features, confidence metadata",
            ),
            PipelineStage(
                name="research",
                description="Inject forecast context into TradingAgents for debate and decision formation.",
                engine="tradingagents",
                output_hint="Normalized research decision and rationale",
            ),
            PipelineStage(
                name="execution_shell",
                description="Surface results through AI Hedge Fund backend, UI, or backtest shell.",
                engine="ai_hedge_fund",
                output_hint="User-facing decision, portfolio action, or backtest output",
            ),
        ]

        tickers = request.tickers or ["AAPL"]
        return self.planned_response(
            f"Hybrid mode is scaffolded for {', '.join(tickers)}. The orchestration pipeline is defined even though the concrete runtime hops are still placeholders.",
            metadata={
                "tickers": tickers,
                "request_options": request.options,
            },
            next_steps=[
                "Normalize forecast outputs into a shared signal schema.",
                "Add a forecast-aware tool or analyst node inside TradingAgents.",
                "Route final signals into ai-hedge-fund backend flows and backtesting.",
            ],
            execution_mode=ExecutionMode.HYBRID_PLAN,
            status=RunStatus.PLANNED,
            pipeline=pipeline,
        )
