from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kronos_hub.workers.common import (
    apply_api_keys,
    bootstrap_project,
    capture_stdio,
    emit_failure,
    emit_result,
    resolve_invocation,
)


def _build_dataframe_from_records(records: list[dict[str, Any]]):
    import pandas as pd

    if not records:
        raise ValueError("Kronos history records cannot be empty.")

    df = pd.DataFrame(records)
    if "timestamps" in df.columns:
        df["timestamps"] = pd.to_datetime(df["timestamps"])
    elif "timestamp" in df.columns:
        df["timestamps"] = pd.to_datetime(df["timestamp"])
    elif "date" in df.columns:
        df["timestamps"] = pd.to_datetime(df["date"])
    else:
        raise ValueError("Each Kronos record must include timestamp/timestamps/date.")

    required_cols = ["open", "high", "low", "close"]
    for column in required_cols:
        if column not in df.columns:
            raise ValueError(f"Missing required price column: {column}")

    if "volume" not in df.columns:
        df["volume"] = 0.0
    if "amount" not in df.columns:
        df["amount"] = 0.0

    numeric_cols = ["open", "high", "low", "close", "volume", "amount"]
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["timestamps", "open", "high", "low", "close"]).reset_index(drop=True)
    return df


def _infer_future_timestamps(df, pred_len: int, payload: dict[str, Any]):
    import pandas as pd

    provided = payload.get("future_timestamps") or []
    if provided:
        future = pd.to_datetime(provided)
        if len(future) != pred_len:
            raise ValueError("future_timestamps length must equal pred_len.")
        return pd.Series(future)

    freq_override = payload.get("future_frequency")
    last_timestamp = df["timestamps"].iloc[-1]
    if freq_override:
        generated = pd.date_range(start=last_timestamp, periods=pred_len + 1, freq=freq_override)[1:]
        return pd.Series(generated)

    inferred = pd.infer_freq(df["timestamps"])
    if inferred:
        generated = pd.date_range(start=last_timestamp, periods=pred_len + 1, freq=inferred)[1:]
        return pd.Series(generated)

    deltas = df["timestamps"].diff().dropna()
    if not deltas.empty:
        step = deltas.iloc[-1]
        return pd.Series([last_timestamp + step * idx for idx in range(1, pred_len + 1)])

    raise ValueError("Unable to infer future timestamps. Provide future_timestamps or future_frequency.")


def _default_tokenizer(model_id: str) -> str:
    lowered = model_id.lower()
    if "mini" in lowered:
        return "NeoQuasar/Kronos-Tokenizer-2k"
    return "NeoQuasar/Kronos-Tokenizer-base"


def _run_prediction(df, payload: dict[str, Any]) -> dict[str, Any]:
    import pandas as pd
    from model import Kronos, KronosPredictor, KronosTokenizer

    apply_api_keys(payload.get("api_keys"))

    pred_len = int(payload.get("pred_len") or 0)
    if pred_len <= 0:
        raise ValueError("pred_len must be a positive integer.")

    lookback = int(payload.get("lookback") or len(df))
    if lookback <= 0:
        raise ValueError("lookback must be positive.")
    if lookback > len(df):
        raise ValueError(f"lookback={lookback} exceeds available rows={len(df)}.")

    working_df = df.tail(lookback).copy().reset_index(drop=True)
    x_timestamp = pd.Series(pd.to_datetime(working_df["timestamps"]))
    y_timestamp = _infer_future_timestamps(working_df, pred_len, payload)

    model_id = payload.get("model_id", "NeoQuasar/Kronos-small")
    tokenizer_id = payload.get("tokenizer_id") or _default_tokenizer(model_id)

    with capture_stdio() as (stdout_buffer, stderr_buffer):
        tokenizer = KronosTokenizer.from_pretrained(tokenizer_id)
        model = Kronos.from_pretrained(model_id)
        predictor = KronosPredictor(
            model,
            tokenizer,
            device=payload.get("device"),
            max_context=int(payload.get("max_context", 512)),
            clip=float(payload.get("clip", 5)),
        )
        pred_df = predictor.predict(
            df=working_df[["open", "high", "low", "close", "volume", "amount"]],
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=float(payload.get("temperature", 1.0)),
            top_k=int(payload.get("top_k", 0)),
            top_p=float(payload.get("top_p", 0.9)),
            sample_count=int(payload.get("sample_count", 1)),
            verbose=bool(payload.get("verbose", False)),
        )

    predictions = []
    for timestamp, row in pred_df.reset_index().rename(columns={"index": "timestamp"}).iterrows():
        predictions.append(
            {
                "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "amount": float(row["amount"]),
            }
        )

    return {
        "model_id": model_id,
        "tokenizer_id": tokenizer_id,
        "device": payload.get("device") or "auto",
        "lookback": lookback,
        "pred_len": pred_len,
        "predictions": predictions,
        "history_window": {
            "start": working_df["timestamps"].iloc[0].isoformat(),
            "end": working_df["timestamps"].iloc[-1].isoformat(),
            "rows": len(working_df),
        },
        "captured_stdout": stdout_buffer.getvalue().strip(),
        "captured_stderr": stderr_buffer.getvalue().strip(),
    }


def predict(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    df = _build_dataframe_from_records(payload.get("history") or [])
    result = _run_prediction(df, payload)
    return {
        "status": "success",
        "service": "kronos",
        "project_root": str(project_root),
        **result,
    }


def predict_batch(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    import pandas as pd
    from model import Kronos, KronosPredictor, KronosTokenizer

    apply_api_keys(payload.get("api_keys"))
    series = payload.get("series") or []
    if not series:
        raise ValueError("Kronos batch prediction requires a non-empty series list.")

    pred_len = int(payload.get("pred_len") or 0)
    if pred_len <= 0:
        raise ValueError("pred_len must be a positive integer.")

    df_list = []
    x_timestamp_list = []
    y_timestamp_list = []
    history_windows = []

    for item in series:
        item_payload = dict(payload)
        item_payload["history"] = item.get("history") or []
        item_payload["future_timestamps"] = item.get("future_timestamps") or payload.get("future_timestamps") or []
        df = _build_dataframe_from_records(item_payload["history"])
        lookback = int(item_payload.get("lookback") or len(df))
        if lookback > len(df):
            raise ValueError(f"lookback={lookback} exceeds available rows={len(df)}.")
        working_df = df.tail(lookback).copy().reset_index(drop=True)
        x_timestamp = pd.Series(pd.to_datetime(working_df["timestamps"]))
        y_timestamp = _infer_future_timestamps(working_df, pred_len, item_payload)
        df_list.append(working_df[["open", "high", "low", "close", "volume", "amount"]])
        x_timestamp_list.append(x_timestamp)
        y_timestamp_list.append(y_timestamp)
        history_windows.append(
            {
                "start": working_df["timestamps"].iloc[0].isoformat(),
                "end": working_df["timestamps"].iloc[-1].isoformat(),
                "rows": len(working_df),
            }
        )

    model_id = payload.get("model_id", "NeoQuasar/Kronos-small")
    tokenizer_id = payload.get("tokenizer_id") or _default_tokenizer(model_id)

    with capture_stdio() as (stdout_buffer, stderr_buffer):
        tokenizer = KronosTokenizer.from_pretrained(tokenizer_id)
        model = Kronos.from_pretrained(model_id)
        predictor = KronosPredictor(
            model,
            tokenizer,
            device=payload.get("device"),
            max_context=int(payload.get("max_context", 512)),
            clip=float(payload.get("clip", 5)),
        )
        pred_df_list = predictor.predict_batch(
            df_list=df_list,
            x_timestamp_list=x_timestamp_list,
            y_timestamp_list=y_timestamp_list,
            pred_len=pred_len,
            T=float(payload.get("temperature", 1.0)),
            top_k=int(payload.get("top_k", 0)),
            top_p=float(payload.get("top_p", 0.9)),
            sample_count=int(payload.get("sample_count", 1)),
            verbose=bool(payload.get("verbose", False)),
        )

    outputs = []
    for pred_df, history_window in zip(pred_df_list, history_windows):
        predictions = []
        for _, row in pred_df.reset_index().rename(columns={"index": "timestamp"}).iterrows():
            predictions.append(
                {
                    "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "amount": float(row["amount"]),
                }
            )
        outputs.append(
            {
                "predictions": predictions,
                "history_window": history_window,
            }
        )

    return {
        "status": "success",
        "service": "kronos",
        "project_root": str(project_root),
        "model_id": model_id,
        "tokenizer_id": tokenizer_id,
        "pred_len": pred_len,
        "series_count": len(outputs),
        "results": outputs,
        "captured_stdout": stdout_buffer.getvalue().strip(),
        "captured_stderr": stderr_buffer.getvalue().strip(),
    }


def main() -> int:
    try:
        action, project_root, payload = resolve_invocation()
        bootstrap_project(project_root)
        if action == "predict":
            emit_result(predict(project_root, payload))
        elif action == "predict_batch":
            emit_result(predict_batch(project_root, payload))
        else:
            raise ValueError(f"Unsupported Kronos action: {action}")
        return 0
    except Exception as exc:
        emit_failure(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
