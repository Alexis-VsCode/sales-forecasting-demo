"""Pronósticos de referencia: valores esperados e índice de fechas futuro."""

from __future__ import annotations

import pandas as pd
import pytest

from sales_forecasting.baselines import (
    moving_average_forecast,
    naive_forecast,
    seasonal_naive_forecast,
)


def _expected_future_index(series: pd.Series, horizon: int) -> pd.DatetimeIndex:
    start = series.index[-1] + pd.offsets.MonthBegin(1)
    return pd.date_range(start, periods=horizon, freq="MS")


def test_naive_repeats_last_value(short_monthly_series):
    fc = naive_forecast(short_monthly_series, 3)
    assert fc.tolist() == [60.0, 60.0, 60.0]


def test_future_index_starts_after_train_and_is_monthly(short_monthly_series):
    fc = naive_forecast(short_monthly_series, 4)
    pd.testing.assert_index_equal(fc.index, _expected_future_index(short_monthly_series, 4))
    assert fc.index.min() > short_monthly_series.index.max()
    assert fc.index[0] == pd.Timestamp("2020-07-01")


def test_seasonal_naive_repeats_last_season(short_monthly_series):
    fc = seasonal_naive_forecast(short_monthly_series, 3, season_length=3)
    assert fc.tolist() == [40.0, 50.0, 60.0]


def test_seasonal_naive_cycles_when_horizon_exceeds_season(short_monthly_series):
    fc = seasonal_naive_forecast(short_monthly_series, 5, season_length=2)
    assert fc.tolist() == [50.0, 60.0, 50.0, 60.0, 50.0]
    pd.testing.assert_index_equal(fc.index, _expected_future_index(short_monthly_series, 5))


def test_seasonal_naive_annual_matches_same_month_last_year(monthly_series):
    fc = seasonal_naive_forecast(monthly_series, 12, season_length=12)
    assert fc.to_numpy() == pytest.approx(monthly_series.iloc[-12:].to_numpy())
    assert (fc.index.month == monthly_series.index[-12:].month).all()


def test_seasonal_naive_requires_a_full_season(short_monthly_series):
    with pytest.raises(ValueError, match="temporada"):
        seasonal_naive_forecast(short_monthly_series, 3, season_length=12)


def test_moving_average_value(short_monthly_series):
    fc = moving_average_forecast(short_monthly_series, 2, window=3)
    assert fc.tolist() == [50.0, 50.0]  # (40 + 50 + 60) / 3
    pd.testing.assert_index_equal(fc.index, _expected_future_index(short_monthly_series, 2))


@pytest.mark.parametrize("window", [0, -1, 7])
def test_moving_average_invalid_window(short_monthly_series, window):
    with pytest.raises(ValueError, match="window"):
        moving_average_forecast(short_monthly_series, 2, window=window)


def test_frequency_is_inferred_when_index_has_no_freq(short_monthly_series):
    no_freq = pd.Series(
        short_monthly_series.to_numpy(), index=pd.DatetimeIndex(list(short_monthly_series.index))
    )
    assert no_freq.index.freq is None
    fc = naive_forecast(no_freq, 2)
    assert fc.index[0] == pd.Timestamp("2020-07-01")


def test_irregular_index_raises():
    index = pd.DatetimeIndex(["2020-01-01", "2020-01-05", "2020-03-17", "2020-08-02"])
    with pytest.raises(ValueError, match="frecuencia"):
        naive_forecast(pd.Series([1.0, 2.0, 3.0, 4.0], index=index), 2)


@pytest.mark.parametrize(
    "func",
    [
        naive_forecast,
        lambda s, h: seasonal_naive_forecast(s, h, season_length=12),
        lambda s, h: moving_average_forecast(s, h, window=3),
    ],
)
def test_all_baselines_have_horizon_length(monthly_series, func):
    fc = func(monthly_series, 7)
    assert len(fc) == 7
    assert fc.notna().all()
