from __future__ import annotations

from enum import Enum


class EngineName(str, Enum):
    AI_HEDGE_FUND = "ai_hedge_fund"
    TRADINGAGENTS = "tradingagents"
    KRONOS = "kronos"
    HYBRID = "hybrid"


class RunStatus(str, Enum):
    READY = "ready"
    STUB = "stub"
    UNAVAILABLE = "unavailable"
    PLANNED = "planned"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionMode(str, Enum):
    ADAPTER = "adapter"
    HANDOFF = "handoff"
    HYBRID_PLAN = "hybrid_plan"
