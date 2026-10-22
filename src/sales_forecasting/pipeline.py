"""Caso de uso de extremo a extremo: ingesta -> agregación -> split -> modelos -> evaluación."""

from __future__ import annotations

import json
import logging
import platform
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels

from . import __version__
from .arima import fit_sarima, forecast, grid_search_arima
from .baselines import moving_average_forecast, naive_forecast, seasonal_naive_forecast
from .config import ForecastConfig
from .data import aggregate_sales, load_sales_csv
from .diagnostics import adf_test, ljung_box_test
from .metrics import evaluate_forecast
from .split import temporal_train_test_split

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    series: pd.Series
    train: pd.Series
    test: pd.Series
    best_order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int]
    order_table: pd.DataFrame
    test_forecasts: pd.DataFrame
    metrics: pd.DataFrame
    ljung_box: pd.DataFrame
    future_forecast: pd.DataFrame
    adf: dict = field(default_factory=dict)
    adf_diff: dict = field(default_factory=dict)


def run_pipeline(config: ForecastConfig) -> PipelineResult:
    np.random.seed(config.seed)  # ARIMA es determinista; se fija por reproducibilidad general
    raw = load_sales_csv(
        config.data_path, config.date_column, config.target_column, config.date_format
    )
    series = aggregate_sales(raw, config.date_column, config.target_column, config.freq)
    logger.info("Serie agregada (%s): %d periodos", config.freq, len(series))

    train, test = temporal_train_test_split(series, config.test_size)
    adf = adf_test(train, config.alpha)
    adf_diff = adf_test(train.diff(config.season_length).dropna(), config.alpha)

    # Selección de orden SOLO con datos de entrenamiento (sin fuga temporal).
    order_table = grid_search_arima(
        train, config.p_values, config.d_values, config.q_values, config.seasonal_order
    )
    best_order = tuple(int(v) for v in order_table.iloc[0]["order"])
    logger.info("Mejor orden ARIMA %s x %s", best_order, config.seasonal_order)

    fitted = fit_sarima(train, best_order, config.seasonal_order)
    arima_fc = forecast(fitted, len(test), config.alpha)
    preds = pd.DataFrame(
        {
            "actual": test,
            f"SARIMA{best_order}x{config.seasonal_order}": arima_fc["forecast"].to_numpy(),
            "Naive": naive_forecast(train, len(test)).to_numpy(),
            "Seasonal naive": seasonal_naive_forecast(
                train, len(test), config.season_length
            ).to_numpy(),
            f"Moving average ({config.moving_average_window})": moving_average_forecast(
                train, len(test), config.moving_average_window
            ).to_numpy(),
        },
        index=test.index,
    )
    preds["lower"] = arima_fc["lower"].to_numpy()
    preds["upper"] = arima_fc["upper"].to_numpy()

    model_cols = [c for c in preds.columns if c not in ("actual", "lower", "upper")]
    metrics = (
        pd.DataFrame({c: evaluate_forecast(preds["actual"], preds[c]) for c in model_cols})
        .T.sort_values("RMSE")
        .rename_axis("modelo")
    )

    # Se omiten los primeros s+d residuos, afectados por la diferenciación inicial.
    burn_in = config.season_length * config.seasonal_order[1] + best_order[1]
    ljung_box = ljung_box_test(fitted.resid.iloc[burn_in:], config.ljung_box_lags)

    # Pronóstico futuro: reentrenar con toda la historia usando el orden ya seleccionado.
    final = fit_sarima(series, best_order, config.seasonal_order)
    future = forecast(final, config.horizon, config.alpha)

    return PipelineResult(
        series=series,
        train=train,
        test=test,
        best_order=best_order,
        seasonal_order=config.seasonal_order,
        order_table=order_table,
        test_forecasts=preds,
        metrics=metrics,
        ljung_box=ljung_box,
        future_forecast=future,
        adf=adf,
        adf_diff=adf_diff,
    )


def environment_info() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "statsmodels": statsmodels.__version__,
        "matplotlib": matplotlib.__version__,
        "sales_forecasting": __version__,
    }


def save_outputs(result: PipelineResult, config: ForecastConfig) -> Path:
    """Persiste métricas, pronósticos y figuras en ``config.output_dir``."""
    out = Path(config.output_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    result.series.to_csv(out / "monthly_sales.csv")
    result.test_forecasts.to_csv(out / "forecast_test.csv")
    result.future_forecast.to_csv(out / "forecast_future.csv", index_label=config.date_column)
    result.metrics.round(4).to_csv(out / "metrics.csv")
    result.order_table.to_csv(out / "arima_grid_search.csv", index=False)

    summary = {
        "data_path": Path(config.data_path).name,
        "freq": config.freq,
        "periods": len(result.series),
        "start": str(result.series.index.min().date()),
        "end": str(result.series.index.max().date()),
        "train_periods": len(result.train),
        "test_periods": len(result.test),
        "test_start": str(result.test.index.min().date()),
        "best_order": list(result.best_order),
        "seasonal_order": list(result.seasonal_order),
        "best_aic": float(result.order_table.iloc[0]["aic"]),
        "adf_train": result.adf,
        "adf_train_seasonal_diff": result.adf_diff,
        "metrics": result.metrics.round(4).to_dict(orient="index"),
        "ljung_box": result.ljung_box.round(4).to_dict(orient="index"),
        "environment": environment_info(),
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    _plot_forecast(result, out / "figures" / "forecast_test.png")
    _plot_future(result, out / "figures" / "forecast_future.png")
    logger.info("Resultados guardados en %s", out)
    return out


def _plot_forecast(result: PipelineResult, path: Path) -> None:
    import matplotlib.pyplot as plt

    preds = result.test_forecasts
    arima_col = next(c for c in preds.columns if c.startswith("SARIMA"))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(result.train.index, result.train, label="Entrenamiento", color="#4C72B0")
    ax.plot(preds.index, preds["actual"], label="Prueba (real)", color="black")
    ax.plot(preds.index, preds[arima_col], label=arima_col, color="#DD8452")
    ax.fill_between(preds.index, preds["lower"], preds["upper"], color="#DD8452", alpha=0.2)
    ax.plot(preds.index, preds["Seasonal naive"], "--", label="Seasonal naive", color="#55A868")
    ax.set(title="Pronóstico vs. real en el periodo de prueba", xlabel="Mes", ylabel="Ventas")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _plot_future(result: PipelineResult, path: Path) -> None:
    import matplotlib.pyplot as plt

    fc = result.future_forecast
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(result.series.index, result.series, label="Histórico", color="#4C72B0")
    ax.plot(fc.index, fc["forecast"], label="Pronóstico", color="#DD8452")
    ax.fill_between(fc.index, fc["lower"], fc["upper"], color="#DD8452", alpha=0.2, label="IC 95%")
    ax.set(title="Pronóstico de ventas de los próximos meses", xlabel="Mes", ylabel="Ventas")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
