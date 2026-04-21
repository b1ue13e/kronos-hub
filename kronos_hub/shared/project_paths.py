from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_ENTRYPOINTS = {
    "ai_hedge_fund": [
        "src/main.py",
        "src/backtester.py",
        "app/backend/main.py",
    ],
    "tradingagents": [
        "main.py",
        "cli/main.py",
        "tradingagents/graph/trading_graph.py",
    ],
    "kronos": [
        "model/kronos.py",
        "webui/app.py",
        "examples/prediction_example.py",
    ],
}


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    root_dir: Path
    ai_hedge_fund: Path
    tradingagents: Path
    kronos: Path

    @classmethod
    def discover(cls, root_dir: Path | None = None) -> "ProjectPaths":
        root = Path(root_dir or Path(__file__).resolve().parents[2]).resolve()
        load_dotenv(root / ".env", override=False)
        return cls(
            root_dir=root,
            ai_hedge_fund=Path(
                os.getenv("KRONOS_HUB_AI_HEDGE_FUND_PATH", str(root / "ai-hedge-fund-main"))
            ).resolve(),
            tradingagents=Path(
                os.getenv("KRONOS_HUB_TRADINGAGENTS_PATH", str(root / "TradingAgents-main"))
            ).resolve(),
            kronos=Path(
                os.getenv("KRONOS_HUB_KRONOS_PATH", str(root / "Kronos-master"))
            ).resolve(),
        )

    def as_mapping(self) -> dict[str, Path]:
        return {
            "ai_hedge_fund": self.ai_hedge_fund,
            "tradingagents": self.tradingagents,
            "kronos": self.kronos,
        }

    def entrypoints_for(self, key: str) -> list[str]:
        return list(DEFAULT_ENTRYPOINTS.get(key, []))
