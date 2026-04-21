from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.engines.adapters.hybrid import HybridAdapter
from kronos_hub.shared.contracts import RunStatus
from kronos_hub.shared.models import RunRequest


class HybridAdapterTest(unittest.TestCase):
    def _build_adapter(self) -> HybridAdapter:
        adapter = HybridAdapter(
            kronos_project_root=ROOT_DIR / "Kronos-master",
            tradingagents_project_root=ROOT_DIR / "TradingAgents-main",
            ai_hedge_fund_project_root=ROOT_DIR / "ai-hedge-fund-main",
        )
        adapter.kronos_service = Mock()
        adapter.trading_research_service = Mock()
        adapter.ai_hedge_fund_service = Mock()
        return adapter

    def test_hybrid_runtime_builds_signal_from_forecast(self) -> None:
        adapter = self._build_adapter()
        adapter.kronos_service.predict.return_value = {
            "predictions": [
                {"timestamp": "2026-01-02T10:00:00", "close": 101.0},
                {"timestamp": "2026-01-02T10:05:00", "close": 103.0},
            ]
        }

        result = adapter.run(
            RunRequest(
                engine="hybrid",
                tickers=["AAPL"],
                dry_run=False,
                options={
                    "history": [
                        {
                            "timestamp": "2026-01-02T09:55:00",
                            "open": 99.0,
                            "high": 100.0,
                            "low": 98.5,
                            "close": 100.0,
                            "volume": 1000.0,
                            "amount": 100000.0,
                        }
                    ],
                    "pred_len": 2,
                },
            )
        )

        self.assertEqual(result.status, RunStatus.COMPLETED.value)
        self.assertEqual(result.result["signal"]["direction"], "bullish")
        self.assertEqual(result.pipeline[0].status, "completed")
        self.assertEqual(result.pipeline[1].status, "skipped")
        self.assertEqual(result.pipeline[2].status, "skipped")

    def test_hybrid_runtime_can_expand_into_research(self) -> None:
        adapter = self._build_adapter()
        adapter.kronos_service.predict.return_value = {
            "predictions": [
                {"timestamp": "2026-01-02T10:00:00", "close": 99.0},
                {"timestamp": "2026-01-02T10:05:00", "close": 98.0},
            ]
        }
        adapter.trading_research_service.run.return_value = {
            "status": "success",
            "decision": "SELL",
        }

        result = adapter.run(
            RunRequest(
                engine="hybrid",
                tickers=["AAPL"],
                trade_date=date(2026, 1, 2),
                dry_run=False,
                options={
                    "history": [
                        {
                            "timestamp": "2026-01-02T09:55:00",
                            "open": 99.0,
                            "high": 100.0,
                            "low": 98.5,
                            "close": 100.0,
                            "volume": 1000.0,
                            "amount": 100000.0,
                        }
                    ],
                    "pred_len": 2,
                    "enable_research": True,
                },
            )
        )

        self.assertEqual(result.status, RunStatus.COMPLETED.value)
        self.assertEqual(result.result["research"]["decision"], "SELL")
        self.assertEqual(result.pipeline[1].status, "completed")
        self.assertEqual(result.result["signal"]["direction"], "bearish")


if __name__ == "__main__":
    unittest.main()
