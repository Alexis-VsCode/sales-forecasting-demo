"""Selección de orden, ajuste y pronóstico ARIMA/SARIMA con statsmodels."""

from __future__ import annotations

import itertools
import logging
import warnings
from collections.abc import Iterable

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults

logger = logging.getLogger(__name__)

Order = tuple[int, int, int]
SeasonalOrder = tuple[int, int, int, int]


def fit_sarima(
    series: pd.Series,
    order: Order,
    seasonal_order: SeasonalOrder = (0, 1, 0, 12),
) -> ARIMAResults:
    """Ajusta SARIMA(order)x(seasonal_order) silenciando avisos de convergencia."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ARIMA(series, order=order, seasonal_order=seasonal_order)
        return model.fit()


def grid_search_arima(
    series: pd.Series,
    p_values: Iterable[int] = range(3),
    d_values: Iterable[int] = range(1, 2),
    q_values: Iterable[int] = range(3),
    seasonal_order: SeasonalOrder = (0, 1, 0, 12),
) -> pd.DataFrame:
    """Evalúa todas las combinaciones (p, d, q) y devuelve una tabla ordenada por AIC."""
    rows = []
    for p, d, q in itertools.product(p_values, d_values, q_values):
        try:
            res = fit_sarima(series, (p, d, q), seasonal_order)
            rows.append({"order": (p, d, q), "aic": float(res.aic), "bic": float(res.bic)})
        except Exception as exc:  # noqa: BLE001 - una combinación inválida no detiene la búsqueda
            logger.warning("Orden %s descartado: %s", (p, d, q), exc)
    if not rows:
        raise RuntimeError("Ninguna combinación ARIMA pudo ajustarse")
    return pd.DataFrame(rows).sort_values("aic", kind="stable").reset_index(drop=True)


def select_arima_order(
    series: pd.Series,
    p_values: range = range(3),
    d_values: range = range(1, 2),
    q_values: range = range(3),
    seasonal_order: SeasonalOrder = (0, 1, 0, 12),
) -> tuple[Order, float]:
    """Devuelve el orden (p, d, q) con menor AIC y su AIC (contrato original del taller)."""
    table = grid_search_arima(series, p_values, d_values, q_values, seasonal_order)
    best = table.iloc[0]
    return tuple(int(v) for v in best["order"]), float(best["aic"])


def forecast(results: ARIMAResults, horizon: int, alpha: float = 0.05) -> pd.DataFrame:
    """Pronóstico puntual con intervalo de confianza (1 - alpha)."""
    pred = results.get_forecast(steps=horizon)
    ci = pred.conf_int(alpha=alpha)
    return pd.DataFrame(
        {
            "forecast": pred.predicted_mean,
            "lower": ci.iloc[:, 0],
            "upper": ci.iloc[:, 1],
        }
    )
