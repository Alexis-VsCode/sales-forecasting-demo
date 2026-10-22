"""Métricas de error con valores calculados a mano."""

from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
import pytest

from sales_forecasting.metrics import evaluate_forecast, mae, mape, rmse, smape, wape

# Caso de referencia: errores absolutos 10, 10 y 30 sobre reales que suman 600.
Y_TRUE = [100.0, 200.0, 300.0]
Y_PRED = [110.0, 190.0, 330.0]


def test_mae_by_hand():
    assert mae(Y_TRUE, Y_PRED) == pytest.approx((10 + 10 + 30) / 3)  # 16.667


def test_rmse_by_hand():
    assert rmse(Y_TRUE, Y_PRED) == pytest.approx(math.sqrt((100 + 100 + 900) / 3))  # 19.149


def test_smape_by_hand():
    expected = 100 * (2 * 10 / 210 + 2 * 10 / 390 + 2 * 30 / 630) / 3  # 8.059 %
    assert smape(Y_TRUE, Y_PRED) == pytest.approx(expected)


def test_wape_by_hand():
    assert wape(Y_TRUE, Y_PRED) == pytest.approx(100 * 50 / 600)  # 8.333 %


def test_mape_by_hand():
    assert mape(Y_TRUE, Y_PRED) == pytest.approx(100 * (0.10 + 0.05 + 0.10) / 3)  # 8.333 %


def test_rmse_is_at_least_mae():
    assert rmse(Y_TRUE, Y_PRED) >= mae(Y_TRUE, Y_PRED)


def test_perfect_forecast_has_zero_error():
    values = [3.0, 0.0, 7.5]
    assert evaluate_forecast(values, values) == {"MAE": 0.0, "RMSE": 0.0, "sMAPE": 0.0, "WAPE": 0.0}


def test_accepts_series_arrays_and_lists():
    expected = mae(Y_TRUE, Y_PRED)
    assert mae(np.array(Y_TRUE), np.array(Y_PRED)) == pytest.approx(expected)
    assert mae(pd.Series(Y_TRUE), pd.Series(Y_PRED)) == pytest.approx(expected)


def test_returns_python_float():
    assert type(rmse(Y_TRUE, Y_PRED)) is float


# --- sMAPE con ceros --------------------------------------------------------------------------


def test_smape_with_zeros_does_not_warn_or_return_nan():
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # un 0/0 emitiría RuntimeWarning
        value = smape([0.0, 0.0, 10.0], [0.0, 5.0, 10.0])
    # pares: 0/0 -> 0 (por convención), 2*5/5 = 2, 0 -> media 2/3
    assert value == pytest.approx(100 * 2 / 3)


def test_smape_all_zeros_is_zero():
    assert smape([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_smape_upper_bound_is_200():
    assert smape([0.0, 0.0], [5.0, 1.0]) == pytest.approx(200.0)


# --- errores ----------------------------------------------------------------------------------


def test_wape_raises_when_actuals_sum_to_zero():
    with pytest.raises(ValueError, match="WAPE"):
        wape([0.0, 0.0], [1.0, 2.0])


def test_mape_raises_with_zero_actuals():
    with pytest.raises(ValueError, match="MAPE"):
        mape([0.0, 1.0], [1.0, 1.0])


@pytest.mark.parametrize("func", [mae, rmse, smape, wape, mape, evaluate_forecast])
def test_different_dimensions_raise(func):
    with pytest.raises(ValueError, match="Dimensiones"):
        func([1.0, 2.0, 3.0], [1.0, 2.0])


@pytest.mark.parametrize("func", [mae, rmse, smape, wape, mape])
def test_empty_inputs_raise(func):
    with pytest.raises(ValueError, match="observaciones"):
        func([], [])


def test_evaluate_forecast_keys_and_values():
    result = evaluate_forecast(Y_TRUE, Y_PRED)
    assert list(result) == ["MAE", "RMSE", "sMAPE", "WAPE"]
    assert result["MAE"] == pytest.approx(mae(Y_TRUE, Y_PRED))
    assert result["WAPE"] == pytest.approx(wape(Y_TRUE, Y_PRED))
