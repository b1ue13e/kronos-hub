from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kronos_hub.api.dependencies import get_registry


router = APIRouter(prefix="/engines", tags=["engines"])


@router.get("")
def list_engines() -> list[dict]:
    return [engine.to_dict() for engine in get_registry().list_engines()]


@router.get("/{engine_name}")
def get_engine(engine_name: str) -> dict:
    registry = get_registry()
    try:
        return registry.get_engine(engine_name).describe().to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
