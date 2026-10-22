"""Partición temporal train/test sin fuga de información."""

from __future__ import annotations

import pandas as pd
import pytest

from sales_forecasting.split import temporal_train_test_split


def test_sizes_and_last_observations_are_test(monthly_series):
    train, test = temporal_train_test_split(monthly_series, 12)
    assert len(train) == 36
    assert len(test) == 12
    pd.testing.assert_series_equal(test, monthly_series.iloc[-12:])
    pd.testing.assert_series_equal(train, monthly_series.iloc[:-12])


def test_no_overlap_and_chronological_order(monthly_series):
    train, test = temporal_train_test_split(monthly_series, 12)
    assert train.index.intersection(test.index).empty
    assert train.index.max() < test.index.min()
    assert train.index.is_monotonic_increasing
    assert test.index.is_monotonic_increasing


def test_split_is_lossless(monthly_series):
    train, test = temporal_train_test_split(monthly_series, 5)
    pd.testing.assert_series_equal(pd.concat([train, test]), monthly_series)


def test_frequency_is_kept(monthly_series):
    train, test = temporal_train_test_split(monthly_series, 12)
    assert train.index.freqstr == "MS"
    assert test.index.freqstr == "MS"


@pytest.mark.parametrize("test_size", [0, -1, 6, 7])
def test_invalid_test_size(short_monthly_series, test_size):
    with pytest.raises(ValueError, match="test_size"):
        temporal_train_test_split(short_monthly_series, test_size)


def test_unsorted_series_is_rejected(short_monthly_series):
    with pytest.raises(ValueError, match="ordenada"):
        temporal_train_test_split(short_monthly_series.iloc[::-1], 2)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "BUG menor en sales_forecasting.split: con fechas duplicadas en el borde train/test la "
        "validación depende de un `assert` (AssertionError, o nada con `python -O`) en vez de "
        "ValueError. Si se corrige, quitar este xfail."
    ),
)
def test_duplicated_timestamp_at_boundary_raises_value_error():
    index = pd.DatetimeIndex(["2020-01-01", "2020-02-01", "2020-02-01", "2020-03-01"])
    series = pd.Series([1.0, 2.0, 3.0, 4.0], index=index)
    with pytest.raises(ValueError):
        temporal_train_test_split(series, 2)
