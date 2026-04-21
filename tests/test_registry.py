from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.engines.registry import EngineRegistry
from kronos_hub.shared.contracts import EngineName
from kronos_hub.shared.models import RunRequest


class EngineRegistryTest(unittest.TestCase):
    def test_discovers_all_subprojects(self) -> None:
        registry = EngineRegistry.from_env(ROOT_DIR)
        projects = {project.key: project for project in registry.list_subprojects()}

        self.assertIn("ai_hedge_fund", projects)
        self.assertIn("tradingagents", projects)
        self.assertIn("kronos", projects)
        self.assertTrue(projects["ai_hedge_fund"].exists)
        self.assertTrue(projects["tradingagents"].exists)
        self.assertTrue(projects["kronos"].exists)

    def test_hybrid_pipeline_has_three_stages(self) -> None:
        registry = EngineRegistry.from_env(ROOT_DIR)
        result = registry.run(
            RunRequest(
                engine=EngineName.HYBRID.value,
                tickers=["AAPL"],
                dry_run=True,
            )
        )

        self.assertEqual(result.engine, EngineName.HYBRID.value)
        self.assertEqual(len(result.pipeline), 3)


if __name__ == "__main__":
    unittest.main()
