from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)


def get_language_instruction() -> str:
    """Return a prompt instruction for the configured output language.

    Returns empty string when English (default), so no extra tokens are used.
    Only applied to user-facing agents (analysts, portfolio manager).
    Internal debate agents stay in English for reasoning quality.
    """
    from tradingagents.dataflows.config import get_config
    lang = get_config().get("output_language", "English")
    if lang.strip().lower() == "english":
        return ""
    return f" Write your entire response in {lang}."


def build_instrument_context(ticker: str) -> str:
    """Describe the exact instrument so agents preserve exchange-qualified tickers."""
    return (
        f"The instrument to analyze is `{ticker}`. "
        "Use this exact ticker in every tool call, report, and recommendation, "
        "preserving any exchange suffix (e.g. `.TO`, `.L`, `.HK`, `.T`)."
    )


def get_hub_forecast_context() -> dict:
    """Return hybrid forecast context injected by the hub, if any."""
    from tradingagents.dataflows.config import get_config

    return dict(get_config().get("hub_forecast_context") or {})


def build_hub_forecast_context_summary(context: dict | None = None) -> str:
    """Format hub forecast context into a concise prompt-ready block."""
    forecast = dict(context or get_hub_forecast_context() or {})
    if not forecast:
        return ""

    direction = forecast.get("direction", "unknown")
    action_bias = forecast.get("action_bias", "unknown")
    expected_return_pct = forecast.get("expected_return_pct", "unknown")
    average_return_pct = forecast.get("average_return_pct", "unknown")
    last_close = forecast.get("last_close", "unknown")
    predicted_last_close = forecast.get("predicted_last_close", "unknown")
    horizon_start = forecast.get("horizon_start", "unknown")
    horizon_end = forecast.get("horizon_end", "unknown")
    narrative = forecast.get("narrative", "")

    return (
        "\nHub Forecast Context:\n"
        f"- Forecast direction: {direction}\n"
        f"- Action bias: {action_bias}\n"
        f"- Last observed close: {last_close}\n"
        f"- Forecasted terminal close: {predicted_last_close}\n"
        f"- Expected return (%): {expected_return_pct}\n"
        f"- Average forecast return (%): {average_return_pct}\n"
        f"- Forecast horizon: {horizon_start} -> {horizon_end}\n"
        f"- Forecast narrative: {narrative}\n"
        "Treat this as additional quantitative context. Do not blindly obey it; weigh it against your own evidence and explicitly mention whether it reinforces or conflicts with your analysis.\n"
    )

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        
