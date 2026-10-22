"""preprocess_ts de la demo H2O (solo pandas: no requiere h2o ni Java)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "h2o_demo" / "src" / "eng_sales_forecasting.py"


@pytest.fixture(scope="module")
def eng():
    spec = importlib.util.spec_from_file_location("h2o_eng_sales_forecasting", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_data_path_is_resolved_from_file(eng, repo_root):
    assert eng.DEFAULT_DATA_PATH == repo_root / "src" / "data" / "stores_sales_forecasting.csv"
    assert eng.DEFAULT_DATA_PATH.is_file()
    assert eng.DEFAULT_OUTPUT_PATH == repo_root / "h2o_demo" / "data" / "aggregated_sales.csv"


def test_monthly_by_default_and_creates_output_dir(eng, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # la ruta de datos no debe depender del cwd
    out = tmp_path / "anidado" / "sub" / "agg.csv"
    returned = eng.preprocess_ts(output_path=out)
    assert isinstance(returned, str)
    assert Path(returned) == out.resolve()
    df = pd.read_csv(returned, parse_dates=["Order Date"])
    assert list(df.columns) == ["Order Date", "Sales"]
    assert len(df) == 48
    assert df["Order Date"].min() == pd.Timestamp("2014-01-01")
    assert (df["Order Date"].dt.day == 1).all()


def test_monthly_total_matches_raw_total(eng, tmp_path):
    raw = pd.read_csv(eng.DEFAULT_DATA_PATH, encoding="latin-1", encoding_errors="replace")
    df = pd.read_csv(eng.preprocess_ts(output_path=tmp_path / "agg.csv"))
    assert df["Sales"].sum() == pytest.approx(raw["Sales"].sum())


def test_weekly_frequency_reproduces_previous_behaviour(eng, tmp_path):
    df = pd.read_csv(eng.preprocess_ts(output_path=tmp_path / "agg_w.csv", freq="W"))
    assert len(df) > 48 * 4  # semanal: muchas más filas que meses


def test_custom_small_dataset(eng, tmp_path):
    src = tmp_path / "mini.csv"
    src.write_bytes("Order Date,Sales\r01/10/2020,5\r03/02/2020,7\r".encode("latin-1"))
    df = pd.read_csv(eng.preprocess_ts(data_path=src, output_path=tmp_path / "o.csv"))
    assert df["Sales"].tolist() == [5, 0, 7]


def test_missing_input_raises(eng, tmp_path):
    with pytest.raises(FileNotFoundError):
        eng.preprocess_ts(data_path=tmp_path / "no.csv", output_path=tmp_path / "o.csv")
