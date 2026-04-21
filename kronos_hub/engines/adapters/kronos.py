from __future__ import annotations

from kronos_hub.engines.base import BaseEngineAdapter
from kronos_hub.shared.contracts import ExecutionMode, RunStatus
from kronos_hub.shared.models import RunRequest, RunResponse
from kronos_hub.shared.worker_client import WorkerExecutionError
from kronos_hub.services.kronos_prediction import KronosPredictionService


class KronosAdapter(BaseEngineAdapter):
    name = "kronos"
    display_name = "Kronos"
    description = "Financial time-series foundation model for OHLCV forecasting, finetuning, and demo visualization."
    capabilities = (
        "ohlcv_forecasting",
        "batch_prediction",
        "finetuning",
        "web_demo",
    )

    def __init__(self, project_root, python_executable: str | None = None):
        super().__init__(project_root)
        self.service = KronosPredictionService(str(self.project_root), python_executable=python_executable)

    def build_command(self, request: RunRequest) -> str:
        pred_len = int(request.options.get("pred_len", 24))
        data_path = request.options.get("data_path", ".\\data\\your_series.csv")
        return (
            "python examples/prediction_example.py "
            f"--data-path {data_path} --pred-len {pred_len}"
        )

    def run(self, request: RunRequest) -> RunResponse:
        if not self.is_available():
            return self.not_available_response(
                "Kronos project directory was not found.",
                next_steps=[
                    "Verify KRONOS_HUB_KRONOS_PATH.",
                    "Confirm Kronos-master exists in the workspace.",
                ],
            )

        command = self.build_command(request)
        if request.dry_run:
            return self.planned_response(
                "Kronos adapter is registered. The hub currently treats it as a forecast engine and reserves a clean service boundary for future inference wiring.",
                metadata={
                    "suggested_command": command,
                    "primary_module": "model/kronos.py",
                    "service_goal": "Refactor into a stable inference service that accepts dataframe-compatible inputs.",
                },
                next_steps=[
                    "Package Kronos into an installable module or service boundary.",
                    "Expose predict and predict_batch through the hub.",
                    "Feed forecast outputs into TradingAgents or AI Hedge Fund as structured signals.",
                ],
                execution_mode=ExecutionMode.HANDOFF,
                status=RunStatus.STUB,
            )

        try:
            options = request.options or {}
            if options.get("series"):
                result = self.service.predict_batch(
                    series=options["series"],
                    pred_len=int(options["pred_len"]),
                    model_id=options.get("model_id", "NeoQuasar/Kronos-small"),
                    tokenizer_id=options.get("tokenizer_id", "NeoQuasar/Kronos-Tokenizer-base"),
                    max_context=int(options.get("max_context", 512)),
                    device=options.get("device"),
                    temperature=float(options.get("temperature", 1.0)),
                    top_k=int(options.get("top_k", 0)),
                    top_p=float(options.get("top_p", 0.9)),
                    sample_count=int(options.get("sample_count", 1)),
                    verbose=bool(options.get("verbose", False)),
                    model_revision=options.get("model_revision"),
                    tokenizer_revision=options.get("tokenizer_revision"),
                    environment={**request.environment, **request.api_keys},
                )
            else:
                result = self.service.predict(
                    history=options["history"],
                    pred_len=int(options["pred_len"]),
                    future_timestamps=options.get("future_timestamps"),
                    model_id=options.get("model_id", "NeoQuasar/Kronos-small"),
                    tokenizer_id=options.get("tokenizer_id", "NeoQuasar/Kronos-Tokenizer-base"),
                    max_context=int(options.get("max_context", 512)),
                    device=options.get("device"),
                    temperature=float(options.get("temperature", 1.0)),
                    top_k=int(options.get("top_k", 0)),
                    top_p=float(options.get("top_p", 0.9)),
                    sample_count=int(options.get("sample_count", 1)),
                    verbose=bool(options.get("verbose", False)),
                    model_revision=options.get("model_revision"),
                    tokenizer_revision=options.get("tokenizer_revision"),
                    environment={**request.environment, **request.api_keys},
                )
            return self.completed_response(
                "Kronos prediction completed through the hub worker runtime.",
                result=result,
                metadata={"worker_mode": "subprocess", "suggested_command": command},
            )
        except KeyError as exc:
            return self.failed_response(
                f"Missing required Kronos option: {exc}",
                next_steps=["Provide 'history' and 'pred_len' for predict, or 'series' and 'pred_len' for batch predict."],
            )
        except WorkerExecutionError as exc:
            return self.failed_response(
                "Kronos worker execution failed.",
                metadata={"stdout": exc.stdout, "stderr": exc.stderr},
                next_steps=[
                    "Check KRONOS_HUB_KRONOS_PYTHON points at an environment with torch, pandas, and huggingface_hub installed.",
                    "Verify the requested model/tokenizer identifiers are reachable.",
                ],
            )
