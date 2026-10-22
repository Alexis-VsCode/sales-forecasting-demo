"""Preprocesamiento de la serie de ventas para la demo de H2O AutoML.

Las rutas por defecto se resuelven relativas a este archivo (no al directorio de
trabajo), de modo que ``preprocess_ts()`` funciona igual si se ejecuta
``python main.py`` desde ``h2o_demo/`` o ``python h2o_demo/main.py`` desde la raíz
del repositorio.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# h2o_demo/src/eng_sales_forecasting.py -> parents[1] = h2o_demo, parents[2] = raíz del repo
_H2O_DEMO_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_PATH = _REPO_ROOT / "src" / "data" / "stores_sales_forecasting.csv"
DEFAULT_OUTPUT_PATH = _H2O_DEMO_DIR / "data" / "aggregated_sales.csv"


def preprocess_ts(
    data_path: str | Path | None = None,
    output_path: str | Path | None = None,
    freq: str = "MS",
    date_column: str = "Order Date",
    target_column: str = "Sales",
    date_format: str | None = "%m/%d/%Y",
) -> str:
    """Agrega las ventas transaccionales por periodo y guarda el resultado en CSV.

    Parámetros
    ----------
    data_path:
        CSV transaccional (latin-1). Por defecto ``<repo>/src/data/stores_sales_forecasting.csv``
        resuelto a partir de la ubicación de este archivo. El CSV original no se modifica.
    output_path:
        CSV de salida. Por defecto ``<repo>/h2o_demo/data/aggregated_sales.csv``. Si el
        directorio no existe, se crea.
    freq:
        Frecuencia de agregación de pandas. Por defecto ``"MS"`` (mensual, inicio de mes),
        coherente con la tarea de ventas mensuales. **Antes** la función usaba ``"W"``
        (semanal) de forma fija; para reproducir ese comportamiento pase ``freq="W"``.
    date_column, target_column:
        Columnas de fecha y de ventas.
    date_format:
        Formato de la fecha (``"%m/%d/%Y"`` en el dataset Superstore). ``None`` deja que
        pandas lo infiera, como hacía la versión original.

    Devuelve
    --------
    str
        Ruta absoluta del CSV generado (``str`` para pasarla directo a ``h2o.import_file``).
    """
    source = Path(data_path) if data_path is not None else DEFAULT_DATA_PATH
    target = Path(output_path) if output_path is not None else DEFAULT_OUTPUT_PATH
    if not source.is_file():
        raise FileNotFoundError(f"No existe el archivo de datos: {source}")

    dataset = pd.read_csv(source, encoding="latin-1", encoding_errors="replace")
    dataset[date_column] = pd.to_datetime(dataset[date_column], format=date_format)
    agg_sales = dataset.groupby(pd.Grouper(key=date_column, freq=freq))[target_column].sum()

    target.parent.mkdir(parents=True, exist_ok=True)
    agg_sales.to_csv(target, index=True)
    return str(target.resolve())
