"""Selección de orden, ajuste y pronóstico SARIMA sobre una serie sintética."""

from __future__ import annotations

import importlib
import importlib.util
import math

import numpy as np
import pandas as pd
import pytest

from sales_forecasting import arima
from sales_forecasting.arima import fit_sarima, forecast, grid_search_arima, select_arima_order

SMALL_GRID = {"p_values": range(2), "d_values": range(1, 2), "q_values": range(2)}


@pytest.fixture(scope="module")
def synthetic_train() -> pd.Series:
    rng = np.random.default_rng(42)
    t = np.arange(36)
    values = 1000 + 10 * t + 200 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 30, t.size)
    return pd.Series(values, index=pd.date_range("2018-01-01", periods=t.size, freq="MS"))


@pytest.fixture(scope="module")
def fitted(synthetic_train):
    return fit_sarima(synthetic_train, (0, 1, 1), (0, 1, 0, 12))


def test_select_arima_order_contract(synthetic_train):
    order, aic = select_arima_order(synthetic_train)
    assert isinstance(order, tuple)
    assert len(order) == 3
    assert all(type(v) is int for v in order)
    assert type(aic) is float
    assert math.isfinite(aic)
    assert order[1] == 1  # d_values=range(1, 2) por defecto


def test_grid_search_is_sorted_by_aic(synthetic_train):
    table = grid_search_arima(synthetic_train, **SMALL_GRID)
    assert list(table.columns) == ["order", "aic", "bic"]
    assert len(table) == 4
    assert table["aic"].is_monotonic_increasing
    assert set(table["order"]) == {(0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1)}


def test_select_matches_first_row_of_grid(synthetic_train):
    table = grid_search_arima(synthetic_train, **SMALL_GRID)
    order, aic = select_arima_order(synthetic_train, **SMALL_GRID)
    assert order == table.iloc[0]["order"]
    assert aic == pytest.approx(table.iloc[0]["aic"])


def test_grid_search_without_candidates_raises(synthetic_train):
    with pytest.raises(RuntimeError, match="Ninguna"):
        grid_search_arima(synthetic_train, p_values=[], d_values=[1], q_values=[0])


def test_fit_sarima_returns_finite_aic(fitted):
    assert math.isfinite(fitted.aic)
    assert len(fitted.resid) == 36


@pytest.mark.parametrize("horizon", [1, 6, 12])
def test_forecast_shape_and_interval_order(fitted, horizon):
    fc = forecast(fitted, horizon)
    assert list(fc.columns) == ["forecast", "lower", "upper"]
    assert len(fc) == horizon
    assert np.isfinite(fc.to_numpy()).all()
    assert (fc["lower"] <= fc["forecast"]).all()
    assert (fc["forecast"] <= fc["upper"]).all()


def test_forecast_index_is_future_monthly(fitted, synthetic_train):
    fc = forecast(fitted, 3)
    expected = pd.date_range("2021-01-01", periods=3, freq="MS")
    pd.testing.assert_index_equal(fc.index, expected, check_names=False)
    assert fc.index.min() > synthetic_train.index.max()


def test_lower_alpha_gives_wider_interval(fitted):
    wide = forecast(fitted, 6, alpha=0.01)
    narrow = forecast(fitted, 6, alpha=0.20)
    assert ((wide["upper"] - wide["lower"]) > (narrow["upper"] - narrow["lower"])).all()
    np.testing.assert_allclose(wide["forecast"], narrow["forecast"])


# --- Shim del contrato original del taller -----------------------------------------------------


def test_arima_trainer_shim_by_file_path(repo_root):
    path = repo_root / "src" / "modeling" / "arima_trainer.py"
    spec = importlib.util.spec_from_file_location("arima_trainer_shim", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.select_arima_order is arima.select_arima_order
    assert module.__all__ == ["select_arima_order"]


def test_arima_trainer_shim_as_module():
    module = importlib.import_module("modeling.arima_trainer")  # pythonpath = ["src"]
    assert module.select_arima_order is select_arima_order
