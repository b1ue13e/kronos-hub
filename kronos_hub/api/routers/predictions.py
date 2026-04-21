from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kronos_hub.api.dependencies import get_kronos_service
from kronos_hub.api.schemas import KronosBatchPredictionRequestBody, KronosPredictionRequestBody
from kronos_hub.shared.worker_client import WorkerExecutionError


router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/kronos")
def predict_kronos(request: KronosPredictionRequestBody) -> dict:
    try:
        return get_kronos_service().predict(
            history=[row.model_dump() for row in request.history],
            pred_len=request.pred_len,
            future_timestamps=request.future_timestamps,
            model_id=request.model_id,
            tokenizer_id=request.tokenizer_id,
            max_context=request.max_context,
            device=request.device,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            sample_count=request.sample_count,
            verbose=request.verbose,
            model_revision=request.model_revision,
            tokenizer_revision=request.tokenizer_revision,
            environment=request.environment,
        )
    except WorkerExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Kronos prediction failed.",
                "stderr": exc.stderr,
                "stdout": exc.stdout,
            },
        ) from exc


@router.post("/kronos/batch")
def predict_kronos_batch(request: KronosBatchPredictionRequestBody) -> dict:
    try:
        return get_kronos_service().predict_batch(
            series=[series.model_dump() for series in request.series],
            pred_len=request.pred_len,
            model_id=request.model_id,
            tokenizer_id=request.tokenizer_id,
            max_context=request.max_context,
            device=request.device,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            sample_count=request.sample_count,
            verbose=request.verbose,
            model_revision=request.model_revision,
            tokenizer_revision=request.tokenizer_revision,
            environment=request.environment,
        )
    except WorkerExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Kronos batch prediction failed.",
                "stderr": exc.stderr,
                "stdout": exc.stdout,
            },
        ) from exc
