"""Pruebas estadísticas: estacionariedad (ADF) y autocorrelación de residuos (Ljung-Box)."""

from __future__ import annotations

import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller


def adf_test(series: pd.Series, alpha: float = 0.05) -> dict[str, float | bool]:
    """Dickey-Fuller aumentado. H0: la serie tiene raíz unitaria (no estacionaria)."""
    stat, pvalue, used_lag, nobs, crit, _ = adfuller(series.dropna(), autolag="AIC")
    return {
        "adf_statistic": float(stat),
        "p_value": float(pvalue),
        "used_lag": int(used_lag),
        "n_obs": int(nobs),
        "critical_5pct": float(crit["5%"]),
        "is_stationary": bool(pvalue < alpha),
    }


def ljung_box_test(residuals: pd.Series, lags: tuple[int, ...] = (6, 12)) -> pd.DataFrame:
    """Ljung-Box. H0: no hay autocorrelación hasta el rezago indicado (residuos ~ ruido blanco)."""
    clean = residuals.dropna()
    valid = [lag for lag in lags if lag < len(clean)]
    if not valid:
        raise ValueError("No hay suficientes residuos para los rezagos solicitados")
    return acorr_ljungbox(clean, lags=valid, return_df=True)
