from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kronos_hub.api.dependencies import get_trading_research_service
from kronos_hub.api.schemas import TradingResearchRequestBody
from kronos_hub.shared.worker_client import WorkerExecutionError


router = APIRouter(prefix="/research", tags=["research"])


@router.post("/tradingagents")
def run_tradingagents_research(request: TradingResearchRequestBody) -> dict:
    try:
        return get_trading_research_service().run(
            ticker=request.ticker,
            trade_date=request.trade_date.isoformat(),
            selected_analysts=request.selected_analysts,
            llm_provider=request.llm_provider,
            deep_think_llm=request.deep_think_llm,
            quick_think_llm=request.quick_think_llm,
            max_debate_rounds=request.max_debate_rounds,
            max_risk_discuss_rounds=request.max_risk_discuss_rounds,
            output_language=request.output_language,
            backend_url=request.backend_url,
            data_vendors=request.data_vendors,
            tool_vendors=request.tool_vendors,
            debug=request.debug,
            config_overrides=request.config_overrides,
            api_keys=request.api_keys,
            environment=request.environment,
        )
    except WorkerExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "TradingAgents research failed.",
                "stderr": exc.stderr,
                "stdout": exc.stdout,
            },
        ) from exc
