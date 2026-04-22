from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TradingAgentsForecastContextSourceTest(unittest.TestCase):
    def test_propagator_seeds_forecast_context_into_state(self) -> None:
        source = (ROOT_DIR / "TradingAgents-main" / "tradingagents" / "graph" / "propagation.py").read_text(encoding="utf-8")
        self.assertIn('"hub_forecast_context"', source)
        self.assertIn('"hub_forecast_summary"', source)
        self.assertIn("build_hub_forecast_context_summary", source)

    def test_agent_utils_exposes_forecast_context_formatter(self) -> None:
        source = (ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "utils" / "agent_utils.py").read_text(encoding="utf-8")
        self.assertIn("def get_hub_forecast_context()", source)
        self.assertIn("def build_hub_forecast_context_summary", source)
        self.assertIn("Treat this as additional quantitative context", source)

    def test_prompt_layers_reference_forecast_context(self) -> None:
        paths = [
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "analysts" / "market_analyst.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "analysts" / "fundamentals_analyst.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "analysts" / "news_analyst.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "analysts" / "social_media_analyst.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "researchers" / "bull_researcher.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "researchers" / "bear_researcher.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "trader" / "trader.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "risk_mgmt" / "aggressive_debator.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "risk_mgmt" / "conservative_debator.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "risk_mgmt" / "neutral_debator.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "managers" / "research_manager.py",
            ROOT_DIR / "TradingAgents-main" / "tradingagents" / "agents" / "managers" / "portfolio_manager.py",
        ]

        for path in paths:
            source = path.read_text(encoding="utf-8")
            self.assertIn("forecast_context", source, msg=f"Missing forecast context in {path.name}")


if __name__ == "__main__":
    unittest.main()
