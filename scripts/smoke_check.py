from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.engines.registry import EngineRegistry
from kronos_hub.shared.contracts import EngineName
from kronos_hub.shared.models import RunRequest


def main() -> int:
    registry = EngineRegistry.from_env(ROOT_DIR)

    print("== Projects ==")
    for project in registry.list_subprojects():
        print(f"- {project.key}: exists={project.exists} path={project.path}")

    print("\n== Engines ==")
    for engine in registry.list_engines():
        print(f"- {engine.name}: available={engine.available} capabilities={','.join(engine.capabilities)}")

    print("\n== Hybrid Dry Run ==")
    result = registry.run(
        RunRequest(
            engine=EngineName.HYBRID.value,
            tickers=["AAPL", "MSFT"],
            dry_run=True,
        )
    )
    print(result.message)
    print(f"stages={len(result.pipeline)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
