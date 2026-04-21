from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


@dataclass(slots=True)
class WorkerExecutionError(RuntimeError):
    worker_script: str
    returncode: int
    stdout: str
    stderr: str

    def __str__(self) -> str:
        return (
            f"Worker '{self.worker_script}' failed with code {self.returncode}. "
            f"stderr={self.stderr.strip() or '<empty>'}"
        )


def get_python_executable(env_var: str) -> str:
    return os.getenv(env_var) or sys.executable


def run_json_worker(
    *,
    worker_script_name: str,
    payload: dict[str, Any],
    python_executable: str | None = None,
    env_overrides: dict[str, str] | None = None,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    root_dir = Path(__file__).resolve().parents[2]
    worker_path = root_dir / "kronos_hub" / "workers" / worker_script_name
    env = os.environ.copy()
    for key, value in (env_overrides or {}).items():
        if value is not None:
            env[str(key)] = str(value)

    process = subprocess.run(
        [python_executable or sys.executable, str(worker_path)],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout_seconds,
        cwd=str(root_dir),
    )
    if process.returncode != 0:
        raise WorkerExecutionError(
            worker_script=worker_script_name,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )

    stdout = process.stdout.strip()
    if not stdout:
        raise WorkerExecutionError(
            worker_script=worker_script_name,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr="Worker produced no stdout payload.",
        )

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise WorkerExecutionError(
            worker_script=worker_script_name,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=f"Invalid JSON worker output: {exc}",
        ) from exc
