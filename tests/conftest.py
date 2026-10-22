"""Fixtures compartidas. Las unitarias usan datos sintéticos en memoria (rápidas y deterministas);
las de integración, marcadas con ``@pytest.mark.integration``, usan el CSV real del repositorio.

Ejecutar solo las rápidas: ``pytest -m "not integration"``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")  # sin pantalla: CI y ejecución local headless

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "forecast.toml"
DATA_PATH = REPO_ROOT / "src" / "data" / "stores_sales_forecasting.csv"
METRICS_JSON = REPO_ROOT / "reports" / "metrics.json"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: prueba de extremo a extremo con el CSV real (más lenta); "
        "excluir con -m 'not integration'",
    )


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def config_path() -> Path:
    return CONFIG_PATH


@pytest.fixture
def transactions_df() -> pd.DataFrame:
    """Transacciones crudas con el esquema del CSV Superstore (fechas como texto %m/%d/%Y).

    Enero y marzo de 2020 tienen ventas; febrero no tiene ninguna transacción.
    """
    return pd.DataFrame(
        {
            "Order Date": ["01/15/2020", "01/20/2020", "03/05/2020", "03/31/2020"],
            "Sales": [10.0, 5.5, 7.0, 3.0],
            "Category": ["Furniture"] * 4,
        }
    )


@pytest.fixture
def monthly_series() -> pd.Series:
    """Serie mensual sintética de 48 meses: tendencia + estacionalidad anual + ruido (seed 42)."""
    rng = np.random.default_rng(42)
    t = np.arange(48)
    values = 1000 + 10 * t + 200 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 30, t.size)
    index = pd.date_range("2018-01-01", periods=t.size, freq="MS", name="Order Date")
    return pd.Series(values, index=index, name="Sales")


@pytest.fixture
def short_monthly_series() -> pd.Series:
    """Serie mensual corta con valores enteros fáciles de verificar a mano."""
    index = pd.date_range("2020-01-01", periods=6, freq="MS")
    return pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 60.0], index=index, name="Sales")


@pytest.fixture
def white_noise() -> pd.Series:
    rng = np.random.default_rng(123)
    return pd.Series(rng.normal(0, 1, 200))


@pytest.fixture
def random_walk() -> pd.Series:
    rng = np.random.default_rng(123)
    return pd.Series(np.cumsum(rng.normal(0, 1, 200)))


@pytest.fixture
def ar1_series() -> pd.Series:
    """AR(1) con phi=0.8: fuertemente autocorrelada."""
    rng = np.random.default_rng(7)
    eps = rng.normal(0, 1, 300)
    values = np.zeros_like(eps)
    for i in range(1, eps.size):
        values[i] = 0.8 * values[i - 1] + eps[i]
    return pd.Series(values)
