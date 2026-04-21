from __future__ import annotations

from functools import lru_cache

from kronos_hub.engines.registry import EngineRegistry
from kronos_hub.services.ai_hedge_fund import AiHedgeFundService
from kronos_hub.services.kronos_prediction import KronosPredictionService
from kronos_hub.services.trading_research import TradingResearchService
from kronos_hub.settings import HubSettings


@lru_cache(maxsize=1)
def get_registry() -> EngineRegistry:
    return EngineRegistry.from_env()


@lru_cache(maxsize=1)
def get_settings() -> HubSettings:
    return HubSettings.from_env()


@lru_cache(maxsize=1)
def get_kronos_service() -> KronosPredictionService:
    settings = get_settings()
    return KronosPredictionService(str(settings.paths.kronos))


@lru_cache(maxsize=1)
def get_trading_research_service() -> TradingResearchService:
    settings = get_settings()
    return TradingResearchService(str(settings.paths.tradingagents))


@lru_cache(maxsize=1)
def get_ai_hedge_fund_service() -> AiHedgeFundService:
    settings = get_settings()
    return AiHedgeFundService(str(settings.paths.ai_hedge_fund))
