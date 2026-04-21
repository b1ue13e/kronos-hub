from __future__ import annotations

from fastapi import APIRouter

from kronos_hub.api.dependencies import get_registry


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects() -> list[dict]:
    return [project.to_dict() for project in get_registry().list_subprojects()]
