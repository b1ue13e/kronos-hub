from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

from kronos_hub.shared.project_paths import ProjectPaths


@dataclass(slots=True)
class HubSettings:
    host: str
    port: int
    paths: ProjectPaths

    @classmethod
    def from_env(cls, root_dir: Path | None = None) -> "HubSettings":
        resolved_root = Path(root_dir or Path(__file__).resolve().parents[1]).resolve()
        load_dotenv(resolved_root / ".env", override=False)
        return cls(
            host=os.getenv("KRONOS_HUB_HOST", "127.0.0.1"),
            port=int(os.getenv("KRONOS_HUB_PORT", "8010")),
            paths=ProjectPaths.discover(root_dir=resolved_root),
        )
