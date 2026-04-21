from __future__ import annotations

from fastapi import APIRouter

from kronos_hub.api.dependencies import get_registry
from kronos_hub.api.schemas import RunRequestBody


router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("")
def run_engine(request: RunRequestBody) -> dict:
    result = get_registry().run(request.to_domain())
    return result.to_dict()
