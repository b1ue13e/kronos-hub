from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.services.ai_hedge_fund import AiHedgeFundService
from kronos_hub.services.kronos_prediction import KronosPredictionService
from kronos_hub.services.trading_research import TradingResearchService


class ServicePayloadTest(unittest.TestCase):
    @patch("kronos_hub.services.kronos_prediction.run_json_worker")
    def test_kronos_predict_payload(self, run_json_worker_mock) -> None:
        run_json_worker_mock.return_value = {"ok": True}
        service = KronosPredictionService("F:/kronos/Kronos-master", python_executable="python-k")

        result = service.predict(
            history=[
                {
                    "timestamp": "2026-01-01T00:00:00",
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                }
            ],
            pred_len=4,
            environment={"HUGGINGFACE_HUB_TOKEN": "secret"},
        )

        self.assertEqual(result, {"ok": True})
        _, kwargs = run_json_worker_mock.call_args
        self.assertEqual(kwargs["worker_script_name"], "kronos_worker.py")
        self.assertEqual(kwargs["python_executable"], "python-k")
        self.assertEqual(kwargs["payload"]["pred_len"], 4)
        self.assertEqual(kwargs["payload"]["command"], "predict")
        self.assertIn("history", kwargs["payload"])
        self.assertEqual(kwargs["env_overrides"]["HUGGINGFACE_HUB_TOKEN"], "secret")

    @patch("kronos_hub.services.trading_research.run_json_worker")
    def test_tradingagents_research_payload(self, run_json_worker_mock) -> None:
        run_json_worker_mock.return_value = {"ok": True, "processed_decision": "BUY"}
        service = TradingResearchService("F:/kronos/TradingAgents-main", python_executable="python-ta")

        result = service.run(
            ticker="NVDA",
            trade_date="2026-01-15",
            selected_analysts=["market", "news"],
            llm_provider="openai",
            deep_think_llm="gpt-5.4",
            api_keys={"OPENAI_API_KEY": "sk-demo"},
        )

        self.assertEqual(result["processed_decision"], "BUY")
        _, kwargs = run_json_worker_mock.call_args
        self.assertEqual(kwargs["worker_script_name"], "tradingagents_worker.py")
        self.assertEqual(kwargs["python_executable"], "python-ta")
        self.assertEqual(kwargs["payload"]["ticker"], "NVDA")
        self.assertEqual(kwargs["payload"]["selected_analysts"], ["market", "news"])
        self.assertEqual(kwargs["payload"]["config_overrides"]["llm_provider"], "openai")
        self.assertEqual(kwargs["payload"]["config_overrides"]["deep_think_llm"], "gpt-5.4")
        self.assertEqual(kwargs["env_overrides"]["OPENAI_API_KEY"], "sk-demo")

    @patch("kronos_hub.services.ai_hedge_fund.run_json_worker")
    def test_ai_hedge_fund_backtest_payload(self, run_json_worker_mock) -> None:
        run_json_worker_mock.return_value = {"ok": True, "mode": "backtest"}
        service = AiHedgeFundService("F:/kronos/ai-hedge-fund-main", python_executable="python-hf")

        result = service.run_backtest(
            tickers=["AAPL", "MSFT"],
            start_date="2025-01-01",
            end_date="2025-03-01",
            initial_capital=250000.0,
            model_name="gpt-4.1",
            model_provider="OpenAI",
            api_keys={"OPENAI_API_KEY": "sk-demo", "FINANCIAL_DATASETS_API_KEY": "fd-demo"},
        )

        self.assertEqual(result["mode"], "backtest")
        _, kwargs = run_json_worker_mock.call_args
        self.assertEqual(kwargs["worker_script_name"], "ai_hedge_fund_worker.py")
        self.assertEqual(kwargs["python_executable"], "python-hf")
        self.assertEqual(kwargs["payload"]["command"], "backtest")
        self.assertEqual(kwargs["payload"]["initial_capital"], 250000.0)
        self.assertEqual(kwargs["env_overrides"]["OPENAI_API_KEY"], "sk-demo")
        self.assertEqual(kwargs["env_overrides"]["FINANCIAL_DATASETS_API_KEY"], "fd-demo")


if __name__ == "__main__":
    unittest.main()
