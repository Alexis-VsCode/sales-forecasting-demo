"""Partición temporal train/test sin fuga de información futura."""

from __future__ import annotations

import pandas as pd


def temporal_train_test_split(series: pd.Series, test_size: int) -> tuple[pd.Series, pd.Series]:
    """Reserva las últimas ``test_size`` observaciones como prueba; nunca baraja."""
    if not series.index.is_monotonic_increasing:
        raise ValueError("La serie debe estar ordenada cronológicamente")
    if not 0 < test_size < len(series):
        raise ValueError(f"test_size debe estar entre 1 y {len(series) - 1}")
    train = series.iloc[: len(series) - test_size]
    test = series.iloc[len(series) - test_size :]
    assert train.index.max() < test.index.min()
    return train, test
