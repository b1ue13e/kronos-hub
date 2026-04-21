from __future__ import annotations

from fastapi import APIRouter

from kronos_hub.api.dependencies import get_registry


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict:
    return get_registry().health().to_dict()
