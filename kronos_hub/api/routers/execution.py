from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kronos_hub.api.dependencies import get_ai_hedge_fund_service
from kronos_hub.api.schemas import AiHedgeFundBacktestRequestBody, AiHedgeFundRunRequestBody
from kronos_hub.shared.worker_client import WorkerExecutionError


router = APIRouter(prefix="/execution", tags=["execution"])


@router.post("/ai-hedge-fund/run")
def run_ai_hedge_fund(request: AiHedgeFundRunRequestBody) -> dict:
    try:
        return get_ai_hedge_fund_service().run_analysis(
            tickers=request.tickers,
            start_date=request.start_date.isoformat() if request.start_date else None,
            end_date=request.end_date.isoformat() if request.end_date else None,
            initial_cash=request.initial_cash,
            margin_requirement=request.margin_requirement,
            selected_analysts=request.selected_analysts,
            model_name=request.model_name,
            model_provider=request.model_provider,
            show_reasoning=request.show_reasoning,
            portfolio_positions=[position.model_dump() for position in request.portfolio_positions],
            api_keys=request.api_keys,
            environment=request.environment,
        )
    except WorkerExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "AI Hedge Fund execution failed.",
                "stderr": exc.stderr,
                "stdout": exc.stdout,
            },
        ) from exc


@router.post("/ai-hedge-fund/backtest")
def backtest_ai_hedge_fund(request: AiHedgeFundBacktestRequestBody) -> dict:
    try:
        return get_ai_hedge_fund_service().run_backtest(
            tickers=request.tickers,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            initial_capital=request.initial_capital,
            margin_requirement=request.margin_requirement,
            selected_analysts=request.selected_analysts,
            model_name=request.model_name,
            model_provider=request.model_provider,
            portfolio_positions=[position.model_dump() for position in request.portfolio_positions],
            api_keys=request.api_keys,
            environment=request.environment,
        )
    except WorkerExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "AI Hedge Fund backtest failed.",
                "stderr": exc.stderr,
                "stdout": exc.stdout,
            },
        ) from exc
