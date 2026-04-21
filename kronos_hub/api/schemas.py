from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from kronos_hub.shared.models import RunRequest


class RunRequestBody(BaseModel):
    engine: str
    tickers: list[str] = Field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    trade_date: date | None = None
    dry_run: bool = True
    api_keys: dict[str, str] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)

    def to_domain(self) -> RunRequest:
        return RunRequest(
            engine=self.engine,
            tickers=self.tickers,
            start_date=self.start_date,
            end_date=self.end_date,
            trade_date=self.trade_date,
            dry_run=self.dry_run,
            api_keys=self.api_keys,
            environment=self.environment,
            options=self.options,
        )


class OHLCVRecord(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    amount: float | None = None


class KronosPredictionRequestBody(BaseModel):
    history: list[OHLCVRecord]
    pred_len: int
    future_timestamps: list[str] = Field(default_factory=list)
    model_id: str = "NeoQuasar/Kronos-small"
    tokenizer_id: str = "NeoQuasar/Kronos-Tokenizer-base"
    max_context: int = 512
    device: str | None = None
    temperature: float = 1.0
    top_k: int = 0
    top_p: float = 0.9
    sample_count: int = 1
    verbose: bool = False
    model_revision: str | None = None
    tokenizer_revision: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)


class KronosBatchSeriesRequestBody(BaseModel):
    history: list[OHLCVRecord]
    future_timestamps: list[str] = Field(default_factory=list)


class KronosBatchPredictionRequestBody(BaseModel):
    series: list[KronosBatchSeriesRequestBody]
    pred_len: int
    model_id: str = "NeoQuasar/Kronos-small"
    tokenizer_id: str = "NeoQuasar/Kronos-Tokenizer-base"
    max_context: int = 512
    device: str | None = None
    temperature: float = 1.0
    top_k: int = 0
    top_p: float = 0.9
    sample_count: int = 1
    verbose: bool = False
    model_revision: str | None = None
    tokenizer_revision: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)


class TradingResearchRequestBody(BaseModel):
    ticker: str
    trade_date: date
    selected_analysts: list[str] = Field(default_factory=lambda: ["market", "social", "news", "fundamentals"])
    llm_provider: str | None = None
    deep_think_llm: str | None = None
    quick_think_llm: str | None = None
    max_debate_rounds: int | None = None
    max_risk_discuss_rounds: int | None = None
    output_language: str | None = None
    backend_url: str | None = None
    data_vendors: dict[str, str] = Field(default_factory=dict)
    tool_vendors: dict[str, str] = Field(default_factory=dict)
    debug: bool = False
    config_overrides: dict[str, Any] = Field(default_factory=dict)
    api_keys: dict[str, str] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)


class PortfolioPositionRequestBody(BaseModel):
    ticker: str
    quantity: float
    trade_price: float


class AiHedgeFundRunRequestBody(BaseModel):
    tickers: list[str]
    start_date: date | None = None
    end_date: date | None = None
    initial_cash: float = 100000.0
    margin_requirement: float = 0.0
    selected_analysts: list[str] = Field(default_factory=list)
    model_name: str = "gpt-4.1"
    model_provider: str = "OpenAI"
    show_reasoning: bool = False
    portfolio_positions: list[PortfolioPositionRequestBody] = Field(default_factory=list)
    api_keys: dict[str, str] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)


class AiHedgeFundBacktestRequestBody(BaseModel):
    tickers: list[str]
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    margin_requirement: float = 0.0
    selected_analysts: list[str] = Field(default_factory=list)
    model_name: str = "gpt-4.1"
    model_provider: str = "OpenAI"
    portfolio_positions: list[PortfolioPositionRequestBody] = Field(default_factory=list)
    api_keys: dict[str, str] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)
