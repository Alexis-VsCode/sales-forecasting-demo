"""Métricas de error de pronóstico."""

from __future__ import annotations

import numpy as np
import pandas as pd

ArrayLike = pd.Series | np.ndarray | list


def _as_arrays(y_true: ArrayLike, y_pred: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(y_true, dtype=float)
    b = np.asarray(y_pred, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"Dimensiones distintas: {a.shape} vs {b.shape}")
    if a.size == 0:
        raise ValueError("No hay observaciones para evaluar")
    return a, b


def mae(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    a, b = _as_arrays(y_true, y_pred)
    return float(np.mean(np.abs(a - b)))


def rmse(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    a, b = _as_arrays(y_true, y_pred)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def smape(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """sMAPE en porcentaje (0-200). Los pares con denominador 0 aportan 0."""
    a, b = _as_arrays(y_true, y_pred)
    denom = np.abs(a) + np.abs(b)
    ratio = np.divide(2 * np.abs(a - b), denom, out=np.zeros_like(denom), where=denom != 0)
    return float(100 * np.mean(ratio))


def wape(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """WAPE en porcentaje: suma de errores absolutos / suma de valores reales."""
    a, b = _as_arrays(y_true, y_pred)
    total = np.sum(np.abs(a))
    if total == 0:
        raise ValueError("WAPE indefinido cuando la suma de valores reales es 0")
    return float(100 * np.sum(np.abs(a - b)) / total)


def mape(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    a, b = _as_arrays(y_true, y_pred)
    if np.any(a == 0):
        raise ValueError("MAPE indefinido con valores reales iguales a 0")
    return float(100 * np.mean(np.abs((a - b) / a)))


def evaluate_forecast(y_true: ArrayLike, y_pred: ArrayLike) -> dict[str, float]:
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
        "WAPE": wape(y_true, y_pred),
    }
