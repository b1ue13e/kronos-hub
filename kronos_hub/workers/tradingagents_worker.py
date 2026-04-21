from __future__ import annotations

import sys
from pathlib import Path


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


def research(project_root: Path, payload: dict) -> dict:
    import os
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env", override=False)
    load_dotenv(project_root / ".env.enterprise", override=False)
    apply_api_keys(payload.get("api_keys"))

    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    config = DEFAULT_CONFIG.copy()
    overrides = dict(payload.get("config_overrides") or {})
    if "data_vendors" in overrides:
        merged_data_vendors = dict(config.get("data_vendors", {}))
        merged_data_vendors.update(overrides.pop("data_vendors") or {})
        config["data_vendors"] = merged_data_vendors
    if "tool_vendors" in overrides:
        merged_tool_vendors = dict(config.get("tool_vendors", {}))
        merged_tool_vendors.update(overrides.pop("tool_vendors") or {})
        config["tool_vendors"] = merged_tool_vendors
    config.update(overrides)

    if config.get("llm_provider", "").lower() == "openai" and not config.get("backend_url"):
        env_backend_url = os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL")
        if env_backend_url:
            config["backend_url"] = env_backend_url

    selected_analysts = payload.get("selected_analysts") or ["market", "social", "news", "fundamentals"]
    ticker = payload["ticker"]
    trade_date = payload["trade_date"]

    with capture_stdio() as (stdout_buffer, stderr_buffer):
        graph = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=bool(payload.get("debug", False)),
            config=config,
        )
        final_state, decision = graph.propagate(ticker, trade_date)

    return {
        "status": "success",
        "service": "tradingagents",
        "project_root": str(project_root),
        "ticker": ticker,
        "trade_date": trade_date,
        "selected_analysts": selected_analysts,
        "decision": decision,
        "reports": {
            "market_report": final_state.get("market_report", ""),
            "sentiment_report": final_state.get("sentiment_report", ""),
            "news_report": final_state.get("news_report", ""),
            "fundamentals_report": final_state.get("fundamentals_report", ""),
            "investment_plan": final_state.get("investment_plan", ""),
            "trader_investment_plan": final_state.get("trader_investment_plan", ""),
            "final_trade_decision": final_state.get("final_trade_decision", ""),
        },
        "config": {
            "llm_provider": config["llm_provider"],
            "deep_think_llm": config["deep_think_llm"],
            "quick_think_llm": config["quick_think_llm"],
            "output_language": config["output_language"],
            "max_debate_rounds": config["max_debate_rounds"],
            "results_dir": config["results_dir"],
        },
        "captured_stdout": stdout_buffer.getvalue().strip(),
        "captured_stderr": stderr_buffer.getvalue().strip(),
    }


def main() -> int:
    try:
        action, project_root, payload = resolve_invocation()
        bootstrap_project(project_root)
        if action != "research":
            raise ValueError(f"Unsupported TradingAgents action: {action}")
        emit_result(research(project_root, payload))
        return 0
    except Exception as exc:
        emit_failure(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
