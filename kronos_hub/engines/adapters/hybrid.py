from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from statistics import mean
from typing import Any

from kronos_hub.engines.base import BaseEngineAdapter
from kronos_hub.services.ai_hedge_fund import AiHedgeFundService
from kronos_hub.services.kronos_prediction import KronosPredictionService
from kronos_hub.services.trading_research import TradingResearchService
from kronos_hub.shared.contracts import ExecutionMode
from kronos_hub.shared.models import PipelineStage, RunRequest, RunResponse
from kronos_hub.shared.worker_client import WorkerExecutionError


class HybridAdapter(BaseEngineAdapter):
    name = "hybrid"
    display_name = "Hybrid Pipeline"
    description = "Forecast-first orchestration mode that can chain Kronos, TradingAgents, and AI Hedge Fund under one contract."
    capabilities = (
        "forecast_plus_research",
        "multi_engine_orchestration",
        "shared_signal_contract",
        "demo_hybrid_chain",
    )

    def __init__(
        self,
        *,
        kronos_project_root: Path | None = None,
        tradingagents_project_root: Path | None = None,
        ai_hedge_fund_project_root: Path | None = None,
        kronos_python_executable: str | None = None,
        tradingagents_python_executable: str | None = None,
        ai_hedge_fund_python_executable: str | None = None,
    ):
        super().__init__(None)
        self.kronos_project_root = kronos_project_root.resolve() if kronos_project_root else None
        self.tradingagents_project_root = tradingagents_project_root.resolve() if tradingagents_project_root else None
        self.ai_hedge_fund_project_root = ai_hedge_fund_project_root.resolve() if ai_hedge_fund_project_root else None

        self.kronos_service = (
            KronosPredictionService(str(self.kronos_project_root), python_executable=kronos_python_executable)
            if self.kronos_project_root
            else None
        )
        self.trading_research_service = (
            TradingResearchService(str(self.tradingagents_project_root), python_executable=tradingagents_python_executable)
            if self.tradingagents_project_root
            else None
        )
        self.ai_hedge_fund_service = (
            AiHedgeFundService(str(self.ai_hedge_fund_project_root), python_executable=ai_hedge_fund_python_executable)
            if self.ai_hedge_fund_project_root
            else None
        )

    def notes(self) -> list[str]:
        notes: list[str] = []
        notes.append(f"Kronos available={self._path_exists(self.kronos_project_root)}")
        notes.append(f"TradingAgents available={self._path_exists(self.tradingagents_project_root)}")
        notes.append(f"AI Hedge Fund available={self._path_exists(self.ai_hedge_fund_project_root)}")
        notes.append("Supports a minimal live demo chain with real forecast + hub-side signal synthesis.")
        return notes

    def run(self, request: RunRequest) -> RunResponse:
        pipeline = self._build_pipeline()
        options = dict(request.options or {})
        tickers = request.tickers or [options.get("ticker", "AAPL")]

        if request.dry_run:
            return self.planned_response(
                f"Hybrid mode is ready for {', '.join(tickers)}. In runtime mode it can execute a real Kronos forecast, synthesize a hub-side signal, and optionally fan out into TradingAgents research and AI Hedge Fund execution/backtesting.",
                metadata={
                    "tickers": tickers,
                    "request_options": options,
                    "demo_request_shape": self._demo_request_shape(),
                },
                next_steps=[
                    "Provide options.history and options.pred_len to run the minimal hybrid demo.",
                    "Set options.enable_research=true with a trade_date to expand into TradingAgents.",
                    "Set options.enable_execution=true with start/end dates to expand into AI Hedge Fund.",
                ],
                execution_mode=ExecutionMode.HYBRID_PLAN,
                pipeline=pipeline,
            )

        ticker = request.tickers[0] if request.tickers else options.get("ticker", "AAPL")
        history = options.get("history") or []
        pred_len = int(options.get("pred_len", 0) or 0)
        if not history or pred_len <= 0:
            return self.failed_response(
                "Hybrid runtime requires options.history and a positive options.pred_len.",
                metadata={"request_options": options},
                next_steps=[
                    "Pass OHLCV rows through options.history.",
                    "Pass the forecast horizon through options.pred_len.",
                    "Use examples/requests/hybrid.demo.template.json as a starting point.",
                ],
            )

        forecast_stage = pipeline[0]
        research_stage = pipeline[1]
        execution_stage = pipeline[2]

        forecast_result: dict[str, Any] = {}
        signal: dict[str, Any] = {}
        research_result: dict[str, Any] = {"status": "skipped", "reason": "enable_research=false"}
        execution_result: dict[str, Any] = {"status": "skipped", "reason": "enable_execution=false"}

        requested_research = bool(options.get("enable_research", False))
        requested_execution = bool(options.get("enable_execution", False))

        try:
            if not self.kronos_service or not self._path_exists(self.kronos_project_root):
                raise RuntimeError("Kronos project path is not available for hybrid runtime.")

            forecast_result = self.kronos_service.predict(
                history=history,
                pred_len=pred_len,
                future_timestamps=options.get("future_timestamps"),
                model_id=options.get("model_id", "NeoQuasar/Kronos-mini"),
                tokenizer_id=options.get("tokenizer_id", "NeoQuasar/Kronos-Tokenizer-2k"),
                max_context=int(options.get("max_context", 256)),
                device=options.get("device"),
                temperature=float(options.get("temperature", 1.0)),
                top_k=int(options.get("top_k", 0)),
                top_p=float(options.get("top_p", 0.9)),
                sample_count=int(options.get("sample_count", 1)),
                verbose=bool(options.get("verbose", False)),
                model_revision=options.get("model_revision"),
                tokenizer_revision=options.get("tokenizer_revision"),
                environment={**request.environment, **request.api_keys, **(options.get("environment") or {})},
            )
            signal = self._build_signal_summary(ticker=ticker, history=history, forecast_result=forecast_result)
            forecast_stage.status = "completed"
            forecast_stage.details = "Real Kronos forecast executed."
            forecast_stage.metadata = {
                "pred_len": pred_len,
                "forecast_direction": signal["direction"],
                "expected_return_pct": signal["expected_return_pct"],
            }
        except (WorkerExecutionError, RuntimeError, ValueError, KeyError) as exc:
            forecast_stage.status = "failed"
            forecast_stage.details = str(exc)
            return self.failed_response(
                "Hybrid runtime could not complete the forecast stage.",
                metadata={"forecast_error": str(exc), "request_options": options},
                next_steps=[
                    "Verify the Kronos worker environment is configured correctly.",
                    "Check that history rows use timestamp/open/high/low/close fields.",
                    "Try the standalone Kronos example first if needed.",
                ],
            )

        if requested_research:
            research_result = self._run_research_stage(
                request=request,
                options=options,
                ticker=ticker,
                signal=signal,
                stage=research_stage,
            )
        else:
            research_stage.status = "skipped"
            research_stage.details = "Research stage not requested."
            research_stage.metadata = {"enable_research": False}

        if requested_execution:
            execution_result = self._run_execution_stage(
                request=request,
                options=options,
                ticker=ticker,
                signal=signal,
                stage=execution_stage,
            )
        else:
            execution_stage.status = "skipped"
            execution_stage.details = "Execution stage not requested."
            execution_stage.metadata = {"enable_execution": False}

        result = {
            "ticker": ticker,
            "forecast": forecast_result,
            "signal": signal,
            "research": research_result,
            "execution": execution_result,
            "hybrid_summary": {
                "bridge_mode": "hub_side_signal_synthesis",
                "forecast_stage": forecast_stage.status,
                "research_stage": research_stage.status,
                "execution_stage": execution_stage.status,
            },
        }

        if requested_research and research_stage.status == "failed":
            return self.partial_response(
                "Hybrid runtime completed the forecast stage, but the requested research stage failed.",
                result=result,
                metadata={"requested_research": True, "requested_execution": requested_execution},
                next_steps=[
                    "Check TradingAgents API keys and provider configuration.",
                    "Retry with options.enable_research=false to validate the minimal forecast demo first.",
                ],
                execution_mode=ExecutionMode.HYBRID_RUNTIME,
                pipeline=pipeline,
            )

        if requested_execution and execution_stage.status == "failed":
            return self.partial_response(
                "Hybrid runtime completed forecast synthesis, but the requested execution stage failed.",
                result=result,
                metadata={"requested_research": requested_research, "requested_execution": True},
                next_steps=[
                    "Check AI Hedge Fund credentials and date range configuration.",
                    "Retry with options.enable_execution=false to validate upstream forecast/research first.",
                ],
                execution_mode=ExecutionMode.HYBRID_RUNTIME,
                pipeline=pipeline,
            )

        message = "Hybrid demo completed with a real forecast and synthesized signal."
        if requested_research and research_stage.status == "completed":
            message += " TradingAgents research was also executed."
        if requested_execution and execution_stage.status == "completed":
            message += " AI Hedge Fund execution/backtesting was also executed."

        return self.completed_response(
            message,
            result=result,
            metadata={
                "requested_research": requested_research,
                "requested_execution": requested_execution,
                "bridge_mode": "hub_side_signal_synthesis",
            },
            execution_mode=ExecutionMode.HYBRID_RUNTIME,
            pipeline=pipeline,
        )

    def _run_research_stage(
        self,
        *,
        request: RunRequest,
        options: dict[str, Any],
        ticker: str,
        signal: dict[str, Any],
        stage: PipelineStage,
    ) -> dict[str, Any]:
        trade_date = request.trade_date or request.end_date
        if not trade_date:
            stage.status = "failed"
            stage.details = "trade_date or end_date is required when enable_research=true."
            return {"status": "failed", "reason": stage.details}
        if not self.trading_research_service or not self._path_exists(self.tradingagents_project_root):
            stage.status = "failed"
            stage.details = "TradingAgents project path is not available."
            return {"status": "failed", "reason": stage.details}

        try:
            config_overrides = deepcopy(options.get("config_overrides") or {})
            config_overrides["hub_forecast_context"] = signal
            result = self.trading_research_service.run(
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
                config_overrides=config_overrides,
                api_keys=request.api_keys,
                environment=request.environment,
            )
            stage.status = "completed"
            stage.details = "TradingAgents research executed."
            stage.metadata = {"ticker": ticker, "trade_date": trade_date.isoformat()}
            return result
        except WorkerExecutionError as exc:
            stage.status = "failed"
            stage.details = "TradingAgents worker execution failed."
            stage.metadata = {"stdout": exc.stdout, "stderr": exc.stderr}
            return {
                "status": "failed",
                "reason": stage.details,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
            }

    def _run_execution_stage(
        self,
        *,
        request: RunRequest,
        options: dict[str, Any],
        ticker: str,
        signal: dict[str, Any],
        stage: PipelineStage,
    ) -> dict[str, Any]:
        if not self.ai_hedge_fund_service or not self._path_exists(self.ai_hedge_fund_project_root):
            stage.status = "failed"
            stage.details = "AI Hedge Fund project path is not available."
            return {"status": "failed", "reason": stage.details}

        tickers = request.tickers or [ticker]
        mode = str(options.get("mode", "run")).lower()
        try:
            if mode == "backtest":
                if not request.start_date or not request.end_date:
                    stage.status = "failed"
                    stage.details = "start_date and end_date are required for backtest execution."
                    return {"status": "failed", "reason": stage.details}
                result = self.ai_hedge_fund_service.run_backtest(
                    tickers=tickers,
                    start_date=request.start_date.isoformat(),
                    end_date=request.end_date.isoformat(),
                    initial_capital=float(options.get("initial_capital", 100000.0)),
                    margin_requirement=float(options.get("margin_requirement", 0.0)),
                    selected_analysts=options.get("execution_selected_analysts") or options.get("selected_analysts"),
                    model_name=options.get("model_name", "gpt-4.1"),
                    model_provider=options.get("model_provider", "OpenAI"),
                    portfolio_positions=options.get("portfolio_positions"),
                    api_keys=request.api_keys,
                    environment=request.environment,
                )
            else:
                if not request.start_date or not request.end_date:
                    stage.status = "failed"
                    stage.details = "start_date and end_date are required for execution."
                    return {"status": "failed", "reason": stage.details}
                result = self.ai_hedge_fund_service.run_analysis(
                    tickers=tickers,
                    start_date=request.start_date.isoformat(),
                    end_date=request.end_date.isoformat(),
                    initial_cash=float(options.get("initial_cash", 100000.0)),
                    margin_requirement=float(options.get("margin_requirement", 0.0)),
                    selected_analysts=options.get("execution_selected_analysts") or options.get("selected_analysts"),
                    model_name=options.get("model_name", "gpt-4.1"),
                    model_provider=options.get("model_provider", "OpenAI"),
                    show_reasoning=bool(options.get("show_reasoning", False)),
                    portfolio_positions=options.get("portfolio_positions"),
                    api_keys=request.api_keys,
                    environment=request.environment,
                )
            stage.status = "completed"
            stage.details = f"AI Hedge Fund {mode} stage executed."
            stage.metadata = {
                "mode": mode,
                "tickers": tickers,
                "forecast_direction": signal["direction"],
            }
            return result
        except WorkerExecutionError as exc:
            stage.status = "failed"
            stage.details = "AI Hedge Fund worker execution failed."
            stage.metadata = {"stdout": exc.stdout, "stderr": exc.stderr, "mode": mode}
            return {
                "status": "failed",
                "reason": stage.details,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
                "mode": mode,
            }

    def _build_pipeline(self) -> list[PipelineStage]:
        return [
            PipelineStage(
                name="forecast",
                description="Generate forecast context from Kronos.",
                engine="kronos",
                output_hint="OHLCV forecast, derived features, confidence metadata",
                status="pending",
            ),
            PipelineStage(
                name="research",
                description="Translate forecast context into a research decision path.",
                engine="tradingagents",
                output_hint="Research decision, rationale, and reports",
                status="pending",
            ),
            PipelineStage(
                name="execution_shell",
                description="Optionally route signals into AI Hedge Fund execution or backtesting.",
                engine="ai_hedge_fund",
                output_hint="User-facing decision, execution, or backtest output",
                status="pending",
            ),
        ]

    def _demo_request_shape(self) -> dict[str, Any]:
        return {
            "engine": "hybrid",
            "tickers": ["AAPL"],
            "dry_run": False,
            "options": {
                "history": "[OHLCV rows]",
                "pred_len": 8,
                "enable_research": False,
                "enable_execution": False,
            },
        }

    def _build_signal_summary(
        self,
        *,
        ticker: str,
        history: list[dict[str, Any]],
        forecast_result: dict[str, Any],
    ) -> dict[str, Any]:
        predictions = forecast_result.get("predictions") or []
        if not predictions:
            raise ValueError("Forecast result contained no predictions.")

        last_close = float(history[-1]["close"])
        predicted_last_close = float(predictions[-1]["close"])
        average_predicted_close = float(mean(float(row["close"]) for row in predictions))
        expected_return_pct = ((predicted_last_close - last_close) / last_close) * 100 if last_close else 0.0
        average_return_pct = ((average_predicted_close - last_close) / last_close) * 100 if last_close else 0.0

        if expected_return_pct >= 1.0:
            direction = "bullish"
            action_bias = "favor_long_bias"
        elif expected_return_pct <= -1.0:
            direction = "bearish"
            action_bias = "favor_defensive_or_short_bias"
        else:
            direction = "neutral"
            action_bias = "favor_wait_or_low_conviction_bias"

        horizon_start = predictions[0]["timestamp"]
        horizon_end = predictions[-1]["timestamp"]
        return {
            "ticker": ticker,
            "direction": direction,
            "action_bias": action_bias,
            "last_close": round(last_close, 6),
            "predicted_last_close": round(predicted_last_close, 6),
            "average_predicted_close": round(average_predicted_close, 6),
            "expected_return_pct": round(expected_return_pct, 4),
            "average_return_pct": round(average_return_pct, 4),
            "pred_len": len(predictions),
            "horizon_start": horizon_start,
            "horizon_end": horizon_end,
            "narrative": (
                f"{ticker} forecast bias is {direction}. "
                f"The last forecast close implies {expected_return_pct:.2f}% expected move versus the last observed close."
            ),
        }

    @staticmethod
    def _path_exists(path_value: Path | None) -> bool:
        return bool(path_value and path_value.exists())
