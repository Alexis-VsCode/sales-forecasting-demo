"""Pruebas ADF y Ljung-Box sobre series sintéticas con semilla fija."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sales_forecasting.diagnostics import adf_test, ljung_box_test

ADF_KEYS = {"adf_statistic", "p_value", "used_lag", "n_obs", "critical_5pct", "is_stationary"}


def test_adf_output_schema(white_noise):
    result = adf_test(white_noise)
    assert set(result) == ADF_KEYS
    assert isinstance(result["is_stationary"], bool)
    assert isinstance(result["used_lag"], int)
    assert 0.0 <= result["p_value"] <= 1.0


def test_adf_white_noise_is_stationary(white_noise):
    result = adf_test(white_noise)
    assert result["is_stationary"] is True
    assert result["p_value"] < 0.05
    assert result["adf_statistic"] < result["critical_5pct"]


def test_adf_random_walk_is_not_stationary(random_walk):
    result = adf_test(random_walk)
    assert result["is_stationary"] is False
    assert result["p_value"] > 0.05


def test_adf_first_difference_of_random_walk_is_stationary(random_walk):
    assert adf_test(random_walk.diff())["is_stationary"] is True  # el NaN inicial se descarta


def test_adf_ignores_missing_values(white_noise):
    with_nan = pd.concat([pd.Series([np.nan, np.nan]), white_noise], ignore_index=True)
    assert adf_test(with_nan)["n_obs"] == adf_test(white_noise)["n_obs"]


def test_adf_alpha_controls_decision(random_walk):
    p_value = adf_test(random_walk)["p_value"]
    assert adf_test(random_walk, alpha=min(0.999, p_value + 0.01))["is_stationary"] is True


def test_ljung_box_white_noise_has_no_autocorrelation(white_noise):
    table = ljung_box_test(white_noise, lags=(6, 12))
    assert list(table.columns) == ["lb_stat", "lb_pvalue"]
    assert list(table.index) == [6, 12]
    assert (table["lb_pvalue"] > 0.05).all()


def test_ljung_box_detects_ar1_autocorrelation(ar1_series):
    table = ljung_box_test(ar1_series, lags=(6, 12))
    assert (table["lb_pvalue"] < 0.01).all()


def test_ljung_box_skips_lags_longer_than_series():
    residuals = pd.Series(np.random.default_rng(0).normal(size=10))
    table = ljung_box_test(residuals, lags=(3, 12))
    assert list(table.index) == [3]


def test_ljung_box_raises_without_enough_residuals():
    with pytest.raises(ValueError, match="residuos"):
        ljung_box_test(pd.Series([0.1, -0.2, 0.3]), lags=(6, 12))
