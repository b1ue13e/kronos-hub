from __future__ import annotations

from typing import Any

from kronos_hub.shared.worker_client import get_python_executable, run_json_worker


class KronosPredictionService:
    def __init__(self, project_root: str, python_executable: str | None = None):
        self.project_root = project_root
        self.python_executable = python_executable or get_python_executable("KRONOS_HUB_KRONOS_PYTHON")

    def predict(
        self,
        *,
        history: list[dict[str, Any]],
        pred_len: int,
        future_timestamps: list[str] | None = None,
        model_id: str = "NeoQuasar/Kronos-small",
        tokenizer_id: str = "NeoQuasar/Kronos-Tokenizer-base",
        max_context: int = 512,
        device: str | None = None,
        temperature: float = 1.0,
        top_k: int = 0,
        top_p: float = 0.9,
        sample_count: int = 1,
        verbose: bool = False,
        model_revision: str | None = None,
        tokenizer_revision: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "command": "predict",
            "project_root": self.project_root,
            "history": history,
            "pred_len": pred_len,
            "future_timestamps": future_timestamps or [],
            "model_id": model_id,
            "tokenizer_id": tokenizer_id,
            "max_context": max_context,
            "device": device,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "sample_count": sample_count,
            "verbose": verbose,
            "model_revision": model_revision,
            "tokenizer_revision": tokenizer_revision,
        }
        return run_json_worker(
            worker_script_name="kronos_worker.py",
            payload=payload,
            python_executable=self.python_executable,
            env_overrides=environment or {},
        )

    def predict_batch(
        self,
        *,
        series: list[dict[str, Any]],
        pred_len: int,
        model_id: str = "NeoQuasar/Kronos-small",
        tokenizer_id: str = "NeoQuasar/Kronos-Tokenizer-base",
        max_context: int = 512,
        device: str | None = None,
        temperature: float = 1.0,
        top_k: int = 0,
        top_p: float = 0.9,
        sample_count: int = 1,
        verbose: bool = False,
        model_revision: str | None = None,
        tokenizer_revision: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "command": "predict_batch",
            "project_root": self.project_root,
            "series": series,
            "pred_len": pred_len,
            "model_id": model_id,
            "tokenizer_id": tokenizer_id,
            "max_context": max_context,
            "device": device,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "sample_count": sample_count,
            "verbose": verbose,
            "model_revision": model_revision,
            "tokenizer_revision": tokenizer_revision,
        }
        return run_json_worker(
            worker_script_name="kronos_worker.py",
            payload=payload,
            python_executable=self.python_executable,
            env_overrides=environment or {},
        )
