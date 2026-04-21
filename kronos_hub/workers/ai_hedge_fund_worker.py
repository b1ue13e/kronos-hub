from __future__ import annotations

from datetime import datetime, timedelta
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.workers.common import (
    apply_api_keys,
    bootstrap_project,
    capture_stdio,
    emit_failure,
    emit_result,
    resolve_invocation,
)


def _normalize_dates(payload: dict) -> tuple[str, str]:
    end_date = payload.get("end_date") or datetime.utcnow().strftime("%Y-%m-%d")
    start_date = payload.get("start_date")
    if not start_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (end_dt - timedelta(days=90)).strftime("%Y-%m-%d")
    return start_date, end_date


def _portfolio_positions(payload: dict) -> list[SimpleNamespace]:
    positions = []
    for item in payload.get("portfolio_positions") or []:
        positions.append(
            SimpleNamespace(
                ticker=item["ticker"],
                quantity=item["quantity"],
                trade_price=item["trade_price"],
            )
        )
    return positions


def _silence_progress() -> None:
    from src.utils.progress import progress

    progress.start = lambda: None
    progress.stop = lambda: None
    progress._refresh_display = lambda: None


def _seed_backtest_positions(backtester, positions: list[SimpleNamespace]) -> None:
    for position in positions:
        ticker = position.ticker
        quantity = float(position.quantity)
        trade_price = float(position.trade_price)
        if quantity > 0:
            backtester._portfolio.apply_long_buy(ticker, int(quantity), trade_price)
        elif quantity < 0:
            backtester._portfolio.apply_short_open(ticker, int(abs(quantity)), trade_price)


def run_once(project_root: Path, payload: dict) -> dict:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env", override=False)
    apply_api_keys(payload.get("api_keys"))
    _silence_progress()

    from app.backend.services.portfolio import create_portfolio
    from src.main import run_hedge_fund

    tickers = payload["tickers"]
    start_date, end_date = _normalize_dates(payload)
    selected_analysts = payload.get("selected_analysts") or []
    positions = _portfolio_positions(payload)

    portfolio = create_portfolio(
        initial_cash=float(payload.get("initial_cash", 100000.0)),
        margin_requirement=float(payload.get("margin_requirement", 0.0)),
        tickers=tickers,
        portfolio_positions=positions,
    )

    with capture_stdio() as (stdout_buffer, stderr_buffer):
        result = run_hedge_fund(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            portfolio=portfolio,
            show_reasoning=bool(payload.get("show_reasoning", False)),
            selected_analysts=selected_analysts,
            model_name=payload.get("model_name", "gpt-4.1"),
            model_provider=payload.get("model_provider", "OpenAI"),
        )

    return {
        "status": "success",
        "service": "ai_hedge_fund",
        "mode": "run",
        "project_root": str(project_root),
        "tickers": tickers,
        "start_date": start_date,
        "end_date": end_date,
        "selected_analysts": selected_analysts,
        "model_name": payload.get("model_name", "gpt-4.1"),
        "model_provider": payload.get("model_provider", "OpenAI"),
        "result": result,
        "captured_stdout": stdout_buffer.getvalue().strip(),
        "captured_stderr": stderr_buffer.getvalue().strip(),
    }


def backtest(project_root: Path, payload: dict) -> dict:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env", override=False)
    apply_api_keys(payload.get("api_keys"))
    _silence_progress()

    from src.backtesting.engine import BacktestEngine
    from src.main import run_hedge_fund

    tickers = payload["tickers"]
    start_date, end_date = _normalize_dates(payload)
    selected_analysts = payload.get("selected_analysts") or []
    positions = _portfolio_positions(payload)

    backtester = BacktestEngine(
        agent=run_hedge_fund,
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_capital=float(payload.get("initial_capital", payload.get("initial_cash", 100000.0))),
        model_name=payload.get("model_name", "gpt-4.1"),
        model_provider=payload.get("model_provider", "OpenAI"),
        selected_analysts=selected_analysts,
        initial_margin_requirement=float(payload.get("margin_requirement", 0.0)),
    )
    if positions:
        _seed_backtest_positions(backtester, positions)

    with capture_stdio() as (stdout_buffer, stderr_buffer):
        performance_metrics = backtester.run_backtest()
        portfolio_values = backtester.get_portfolio_values()

    normalized_values = []
    for point in portfolio_values:
        normalized_values.append(
            {
                "date": point["Date"].isoformat() if hasattr(point["Date"], "isoformat") else str(point["Date"]),
                "portfolio_value": float(point["Portfolio Value"]),
                "long_exposure": float(point.get("Long Exposure", 0.0)),
                "short_exposure": float(point.get("Short Exposure", 0.0)),
                "gross_exposure": float(point.get("Gross Exposure", 0.0)),
                "net_exposure": float(point.get("Net Exposure", 0.0)),
                "long_short_ratio": float(point.get("Long/Short Ratio", 0.0)),
            }
        )

    final_value = normalized_values[-1]["portfolio_value"] if normalized_values else float(payload.get("initial_capital", 100000.0))

    return {
        "status": "success",
        "service": "ai_hedge_fund",
        "mode": "backtest",
        "project_root": str(project_root),
        "tickers": tickers,
        "start_date": start_date,
        "end_date": end_date,
        "selected_analysts": selected_analysts,
        "model_name": payload.get("model_name", "gpt-4.1"),
        "model_provider": payload.get("model_provider", "OpenAI"),
        "performance_metrics": performance_metrics,
        "portfolio_values": normalized_values,
        "final_portfolio_value": final_value,
        "captured_stdout": stdout_buffer.getvalue().strip(),
        "captured_stderr": stderr_buffer.getvalue().strip(),
    }


def main() -> int:
    try:
        action, project_root, payload = resolve_invocation()
        bootstrap_project(project_root)
        if action == "run":
            emit_result(run_once(project_root, payload))
        elif action == "backtest":
            emit_result(backtest(project_root, payload))
        else:
            raise ValueError(f"Unsupported AI Hedge Fund action: {action}")
        return 0
    except Exception as exc:
        emit_failure(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
