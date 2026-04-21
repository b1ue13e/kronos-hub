from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import date, datetime
import io
import json
import os
from pathlib import Path
import sys
import traceback
from typing import Any, Iterator


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def bootstrap_project(project_root: Path) -> None:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def resolve_invocation() -> tuple[str, Path, dict[str, Any]]:
    payload = read_payload()
    action = sys.argv[1] if len(sys.argv) > 1 else payload.get("command")
    project_root_value = sys.argv[2] if len(sys.argv) > 2 else payload.get("project_root")
    if not action:
        raise ValueError("Worker action/command is required.")
    if not project_root_value:
        raise ValueError("Worker project_root is required.")
    return action, Path(project_root_value).resolve(), payload


def json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def emit_result(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, default=json_default))


def emit_failure(exc: BaseException) -> None:
    message = {
        "error": str(exc),
        "exception_type": exc.__class__.__name__,
    }
    print(json.dumps(message, ensure_ascii=False), file=sys.stderr)
    traceback.print_exc(file=sys.stderr)


@contextmanager
def capture_stdio() -> Iterator[tuple[io.StringIO, io.StringIO]]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        yield stdout_buffer, stderr_buffer


def apply_api_keys(api_keys: dict[str, str] | None) -> None:
    for key, value in (api_keys or {}).items():
        if value:
            os.environ[key] = value


def resolve_path(path_value: str | None, project_root: Path) -> Path | None:
    if not path_value:
        return None
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    direct = (project_root / candidate).resolve()
    if direct.exists():
        return direct
    return (ROOT_DIR / candidate).resolve()
