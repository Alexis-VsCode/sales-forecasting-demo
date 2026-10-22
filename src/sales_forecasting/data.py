"""Ingesta, validación y agregación temporal de las ventas (sin modificar el CSV original)."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidationError(ValueError):
    """Los datos de entrada no cumplen el esquema esperado."""


def load_sales_csv(
    path: str | Path,
    date_column: str = "Order Date",
    target_column: str = "Sales",
    date_format: str = "%m/%d/%Y",
) -> pd.DataFrame:
    """Lee el CSV transaccional (latin-1, fin de línea CR) y valida columnas, fechas y ventas."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de datos: {path}")
    df = pd.read_csv(path, encoding="latin-1", encoding_errors="replace")
    return validate_sales(df, date_column, target_column, date_format)


def validate_sales(
    df: pd.DataFrame,
    date_column: str = "Order Date",
    target_column: str = "Sales",
    date_format: str = "%m/%d/%Y",
) -> pd.DataFrame:
    """Devuelve una copia con fecha parseada y ventas numéricas; falla si el esquema es inválido."""
    missing = {date_column, target_column} - set(df.columns)
    if missing:
        raise DataValidationError(f"Faltan columnas obligatorias: {sorted(missing)}")
    if df.empty:
        raise DataValidationError("El dataset está vacío")
    out = df.copy()
    try:
        out[date_column] = pd.to_datetime(out[date_column], format=date_format)
    except (ValueError, TypeError) as exc:
        raise DataValidationError(f"Fechas inválidas en '{date_column}': {exc}") from exc
    out[target_column] = pd.to_numeric(out[target_column], errors="coerce")
    n_null = int(out[target_column].isna().sum())
    if n_null:
        raise DataValidationError(f"{n_null} valores no numéricos o vacíos en '{target_column}'")
    if (out[target_column] < 0).any():
        raise DataValidationError(f"Existen ventas negativas en '{target_column}'")
    logger.info(
        "Datos validados: %d filas, %s a %s",
        len(out),
        out[date_column].min().date(),
        out[date_column].max().date(),
    )
    return out


def aggregate_sales(
    df: pd.DataFrame,
    date_column: str = "Order Date",
    target_column: str = "Sales",
    freq: str = "MS",
) -> pd.Series:
    """Suma las ventas por periodo; periodos sin transacciones quedan en 0 (frecuencia regular)."""
    series = df.groupby(pd.Grouper(key=date_column, freq=freq))[target_column].sum()
    series = series.asfreq(freq, fill_value=0.0).astype(float)
    series.name = target_column
    series.index.name = date_column
    return series
