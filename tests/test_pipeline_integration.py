"""Integración de extremo a extremo con el CSV real y configs/forecast.toml.

Marcadas ``integration``: ``pytest -m "not integration"`` las omite.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from sales_forecasting.config import load_config
from sales_forecasting.pipeline import run_pipeline

pytestmark = pytest.mark.integration

MODEL_PREFIXES = ("SARIMA", "Naive", "Seasonal naive", "Moving average")


@pytest.fixture(scope="module")
def result():
    from pathlib import Path

    config = load_config(Path(__file__).resolve().parents[1] / "configs" / "forecast.toml")
    return run_pipeline(config)


def test_monthly_series_and_split_sizes(result):
    assert len(result.series) == 48
    assert result.series.index.freqstr == "MS"
    assert result.series.index.min() == pd.Timestamp("2014-01-01")
    assert result.series.index.max() == pd.Timestamp("2017-12-01")
    assert len(result.train) == 36
    assert len(result.test) == 12


def test_no_temporal_leakage(result):
    assert result.train.index.max() < result.test.index.min()
    assert result.train.index.max() == pd.Timestamp("2016-12-01")
    assert result.test.index.min() == pd.Timestamp("2017-01-01")
    pd.testing.assert_series_equal(pd.concat([result.train, result.test]), result.series)


def test_metrics_are_finite_for_all_models(result):
    metrics = result.metrics
    assert list(metrics.columns) == ["MAE", "RMSE", "sMAPE", "WAPE"]
    assert len(metrics) == 4
    for prefix in MODEL_PREFIXES:
        assert any(name.startswith(prefix) for name in metrics.index), prefix
    assert np.isfinite(metrics.to_numpy()).all()
    assert (metrics.to_numpy() >= 0).all()
    assert metrics["RMSE"].is_monotonic_increasing  # tabla ordenada por RMSE


def test_best_order_comes_from_grid(result):
    assert result.best_order == result.order_table.iloc[0]["order"]
    assert result.order_table["aic"].is_monotonic_increasing
    assert result.seasonal_order == (0, 1, 0, 12)


def test_test_forecasts_are_aligned_with_test(result):
    preds = result.test_forecasts
    pd.testing.assert_index_equal(preds.index, result.test.index)
    np.testing.assert_allclose(preds["actual"], result.test)
    arima_col = next(c for c in preds.columns if c.startswith("SARIMA"))
    assert (preds["lower"] <= preds[arima_col]).all()
    assert (preds[arima_col] <= preds["upper"]).all()


def test_future_forecast_starts_after_history(result):
    future = result.future_forecast
    assert len(future) == 12
    assert future.index.min() == pd.Timestamp("2018-01-01")
    assert (future["lower"] <= future["forecast"]).all()
    assert (future["forecast"] <= future["upper"]).all()


def test_ljung_box_lags(result):
    assert list(result.ljung_box.index) == [6, 12]
    assert result.ljung_box["lb_pvalue"].between(0, 1).all()


def test_results_match_committed_reports(result, repo_root):
    """Los números de reports/metrics.json deben poder regenerarse con el código actual."""
    committed = json.loads((repo_root / "reports" / "metrics.json").read_text(encoding="utf-8"))
    assert committed["periods"] == len(result.series)
    assert committed["train_periods"] == len(result.train)
    assert committed["test_periods"] == len(result.test)
    assert tuple(committed["best_order"]) == result.best_order
    assert committed["best_aic"] == pytest.approx(float(result.order_table.iloc[0]["aic"]), 1e-6)
    for model, values in committed["metrics"].items():
        for metric, value in values.items():
            assert result.metrics.loc[model, metric] == pytest.approx(value, rel=1e-3), (
                model,
                metric,
            )
    for lag, values in committed["ljung_box"].items():
        observed = result.ljung_box.loc[int(lag), "lb_pvalue"]
        assert observed == pytest.approx(values["lb_pvalue"], abs=1e-3)


def test_cli_smoke_writes_outputs_to_custom_dir(tmp_path, repo_root, config_path):
    out_dir = tmp_path / "ci-reports"
    committed_metrics = repo_root / "reports" / "metrics.json"
    mtime_before = committed_metrics.stat().st_mtime_ns

    env = {**os.environ, "MPLBACKEND": "Agg"}
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "sales_forecasting",
            "--config",
            str(config_path),
            "--output-dir",
            str(out_dir),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Mejor modelo: SARIMA" in proc.stdout

    for name in (
        "metrics.json",
        "metrics.csv",
        "monthly_sales.csv",
        "forecast_test.csv",
        "forecast_future.csv",
        "arima_grid_search.csv",
    ):
        assert (out_dir / name).is_file(), name
    figures = sorted((out_dir / "figures").glob("*.png"))
    assert {p.name for p in figures} == {"forecast_test.png", "forecast_future.png"}
    for png in figures:
        assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    summary = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert (summary["periods"], summary["train_periods"], summary["test_periods"]) == (48, 36, 12)
    assert summary["freq"] == "MS"
    assert len(pd.read_csv(out_dir / "monthly_sales.csv")) == 48
    assert len(pd.read_csv(out_dir / "forecast_test.csv")) == 12

    # --output-dir no debe tocar los reportes versionados del repositorio.
    assert committed_metrics.stat().st_mtime_ns == mtime_before
