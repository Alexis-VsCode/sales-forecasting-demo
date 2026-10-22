"""Ingesta, validación de esquema y agregación mensual."""

from __future__ import annotations

import pandas as pd
import pytest

from sales_forecasting.data import (
    DataValidationError,
    aggregate_sales,
    load_sales_csv,
    validate_sales,
)

# --- validate_sales ---------------------------------------------------------------------------


def test_validate_parses_dates_and_numeric_sales(transactions_df):
    df = transactions_df.assign(Sales=["10", "5.5", 7, 3.0])
    out = validate_sales(df)
    assert pd.api.types.is_datetime64_any_dtype(out["Order Date"])
    assert pd.api.types.is_float_dtype(out["Sales"])
    assert out["Sales"].tolist() == [10.0, 5.5, 7.0, 3.0]
    assert out["Order Date"].iloc[0] == pd.Timestamp("2020-01-15")


def test_validate_returns_copy_without_mutating_input(transactions_df):
    original = transactions_df.copy()
    validate_sales(transactions_df)
    pd.testing.assert_frame_equal(transactions_df, original)


def test_validation_error_is_value_error():
    assert issubclass(DataValidationError, ValueError)


@pytest.mark.parametrize("missing", ["Order Date", "Sales"])
def test_missing_required_column(transactions_df, missing):
    with pytest.raises(DataValidationError, match="Faltan columnas") as exc:
        validate_sales(transactions_df.drop(columns=missing))
    assert missing in str(exc.value)


def test_missing_both_columns():
    with pytest.raises(DataValidationError, match="Order Date.*Sales"):
        validate_sales(pd.DataFrame({"x": [1]}))


def test_custom_column_names(transactions_df):
    df = transactions_df.rename(columns={"Order Date": "fecha", "Sales": "ventas"})
    out = validate_sales(df, date_column="fecha", target_column="ventas")
    assert out["ventas"].sum() == pytest.approx(25.5)


def test_empty_dataset():
    with pytest.raises(DataValidationError, match="vacío"):
        validate_sales(pd.DataFrame({"Order Date": [], "Sales": []}))


@pytest.mark.parametrize("bad_date", ["13/45/2020", "2020-01-15", "no es fecha"])
def test_invalid_dates(transactions_df, bad_date):
    df = transactions_df.copy()
    df.loc[1, "Order Date"] = bad_date
    with pytest.raises(DataValidationError, match="Fechas inválidas"):
        validate_sales(df)


@pytest.mark.parametrize("empty_date", [None, ""])
def test_empty_dates_are_rejected(transactions_df, empty_date):
    df = transactions_df.copy()
    df.loc[1, "Order Date"] = empty_date
    with pytest.raises(DataValidationError):
        validate_sales(df)


@pytest.mark.parametrize("bad_value", ["abc", None, float("nan")])
def test_non_numeric_or_missing_sales(transactions_df, bad_value):
    df = transactions_df.astype({"Sales": object})
    df.loc[2, "Sales"] = bad_value
    with pytest.raises(DataValidationError, match="no numéricos"):
        validate_sales(df)


def test_negative_sales(transactions_df):
    df = transactions_df.copy()
    df.loc[0, "Sales"] = -0.01
    with pytest.raises(DataValidationError, match="negativas"):
        validate_sales(df)


def test_zero_sales_are_valid(transactions_df):
    df = transactions_df.copy()
    df.loc[0, "Sales"] = 0.0
    assert validate_sales(df)["Sales"].iloc[0] == 0.0


# --- aggregate_sales --------------------------------------------------------------------------


def test_monthly_aggregation_sums_and_fills_empty_months(transactions_df):
    series = aggregate_sales(validate_sales(transactions_df), freq="MS")
    expected_index = pd.date_range("2020-01-01", "2020-03-01", freq="MS")
    pd.testing.assert_index_equal(series.index, expected_index, check_names=False)
    assert series.tolist() == [15.5, 0.0, 10.0]  # febrero sin transacciones -> 0
    assert series.index.freqstr == "MS"
    assert series.name == "Sales"
    assert series.index.name == "Order Date"
    assert series.dtype == float


def test_aggregation_preserves_total(transactions_df):
    validated = validate_sales(transactions_df)
    assert aggregate_sales(validated).sum() == pytest.approx(validated["Sales"].sum())


def test_aggregation_is_regular_without_gaps(transactions_df):
    series = aggregate_sales(validate_sales(transactions_df))
    assert series.index.is_monotonic_increasing
    assert len(series) == len(pd.date_range(series.index[0], series.index[-1], freq="MS"))


def test_weekly_frequency_is_still_available(transactions_df):
    series = aggregate_sales(validate_sales(transactions_df), freq="W")
    assert series.index.freqstr.startswith("W")
    assert len(series) > 3  # más periodos que la agregación mensual


# --- load_sales_csv ---------------------------------------------------------------------------


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales_csv(tmp_path / "no_existe.csv")


def test_load_latin1_with_cr_line_endings(tmp_path):
    """El CSV real es latin-1 con fin de línea CR; se replica en pequeño."""
    content = "Order Date,Sales,City\r01/02/2020,10.5,Bogotá\r02/03/2020,4,Medellín\r"
    path = tmp_path / "ventas.csv"
    path.write_bytes(content.encode("latin-1"))
    df = load_sales_csv(path)
    assert len(df) == 2
    assert df["City"].tolist() == ["Bogotá", "Medellín"]
    assert df["Sales"].sum() == pytest.approx(14.5)


def test_real_dataset_contract(repo_root):
    """Contrato del dataset del taller (lectura rápida; no se modifica el CSV)."""
    df = load_sales_csv(repo_root / "src" / "data" / "stores_sales_forecasting.csv")
    assert len(df) == 2121
    assert set(df["Category"].unique()) == {"Furniture"}
    assert df["Order Date"].min() == pd.Timestamp("2014-01-06")
    assert df["Order Date"].max() == pd.Timestamp("2017-12-30")
    assert len(aggregate_sales(df)) == 48
