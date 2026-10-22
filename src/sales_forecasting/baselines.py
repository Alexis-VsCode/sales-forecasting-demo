"""Pronósticos de referencia (baselines) que el modelo ARIMA debe superar."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _future_index(train: pd.Series, horizon: int) -> pd.DatetimeIndex:
    freq = train.index.freq or pd.infer_freq(train.index)
    if freq is None:
        raise ValueError("No se pudo inferir la frecuencia de la serie")
    return pd.date_range(train.index[-1], periods=horizon + 1, freq=freq)[1:]


def naive_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """Repite el último valor observado."""
    return pd.Series(np.repeat(train.iloc[-1], horizon), index=_future_index(train, horizon))


def seasonal_naive_forecast(train: pd.Series, horizon: int, season_length: int = 12) -> pd.Series:
    """Repite el valor del mismo periodo de la temporada anterior."""
    if len(train) < season_length:
        raise ValueError("La serie es más corta que una temporada")
    last_season = train.iloc[-season_length:].to_numpy()
    values = np.resize(last_season, horizon)
    return pd.Series(values, index=_future_index(train, horizon))


def moving_average_forecast(train: pd.Series, horizon: int, window: int = 3) -> pd.Series:
    """Promedio de las últimas ``window`` observaciones, constante en el horizonte."""
    if window <= 0 or window > len(train):
        raise ValueError("window debe estar entre 1 y len(train)")
    value = float(train.iloc[-window:].mean())
    return pd.Series(np.repeat(value, horizon), index=_future_index(train, horizon))
