"""Carga de configuración TOML y validaciones de ForecastConfig."""

from __future__ import annotations

import dataclasses
import tomllib
from pathlib import Path

import pytest

from sales_forecasting.config import PROJECT_ROOT, ForecastConfig, load_config


def test_project_root_is_repo_root(repo_root):
    assert PROJECT_ROOT == repo_root


def test_load_repo_toml_matches_file(config_path, repo_root):
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    cfg = load_config(config_path)
    assert cfg.data_path == (repo_root / raw["data"]["path"]).resolve()
    assert cfg.data_path.is_file()
    assert cfg.output_dir == (repo_root / raw["output"]["output_dir"]).resolve()
    assert cfg.date_column == raw["data"]["date_column"]
    assert cfg.target_column == raw["data"]["target_column"]
    assert cfg.date_format == raw["data"]["date_format"]
    assert cfg.freq == raw["data"]["freq"]
    assert cfg.test_size == raw["split"]["test_size"]
    assert cfg.horizon == raw["split"]["horizon"]
    assert cfg.p_values == tuple(raw["model"]["p_values"])
    assert cfg.d_values == tuple(raw["model"]["d_values"])
    assert cfg.q_values == tuple(raw["model"]["q_values"])
    assert cfg.seasonal_order == tuple(raw["model"]["seasonal_order"])
    assert cfg.season_length == raw["model"]["season_length"]
    assert cfg.moving_average_window == raw["model"]["moving_average_window"]
    assert cfg.seed == raw["model"]["seed"]
    assert cfg.alpha == raw["diagnostics"]["alpha"]
    assert cfg.ljung_box_lags == tuple(raw["diagnostics"]["ljung_box_lags"])


def test_repo_toml_is_monthly_with_12_month_holdout(config_path):
    cfg = load_config(config_path)
    assert cfg.freq == "MS"
    assert cfg.test_size == 12
    assert len(cfg.seasonal_order) == 4
    assert cfg.seasonal_order[3] == cfg.season_length == 12


def test_load_config_without_path_returns_defaults():
    assert load_config(None) == ForecastConfig()


def test_relative_paths_resolve_against_project_root(tmp_path):
    toml = tmp_path / "cfg.toml"
    toml.write_text('[data]\npath = "src/data/x.csv"\n[output]\noutput_dir = "out"\n')
    cfg = load_config(toml)
    assert cfg.data_path == PROJECT_ROOT / "src" / "data" / "x.csv"
    assert cfg.output_dir == PROJECT_ROOT / "out"


def test_absolute_paths_are_kept(tmp_path):
    toml = tmp_path / "cfg.toml"
    data = tmp_path / "ventas.csv"
    toml.write_text(f'[data]\npath = "{data.as_posix()}"\n[split]\ntest_size = 6\n')
    cfg = load_config(toml)
    assert cfg.data_path == data
    assert cfg.test_size == 6
    assert cfg.horizon == ForecastConfig().horizon  # claves ausentes -> valores por defecto


def test_missing_toml_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "no_existe.toml")


def test_config_is_frozen():
    cfg = ForecastConfig()
    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.test_size = 3  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("test_size", 0, "test_size"),
        ("test_size", -3, "test_size"),
        ("horizon", 0, "horizon"),
        ("alpha", 0.0, "alpha"),
        ("alpha", 1.0, "alpha"),
        ("alpha", 1.5, "alpha"),
        ("seasonal_order", (0, 1, 12), "seasonal_order"),
    ],
)
def test_post_init_validations(field, value, message):
    with pytest.raises(ValueError, match=message):
        ForecastConfig(**{field: value})


def test_invalid_toml_value_is_rejected(tmp_path):
    toml = tmp_path / "cfg.toml"
    toml.write_text("[diagnostics]\nalpha = 2.0\n")
    with pytest.raises(ValueError, match="alpha"):
        load_config(toml)


def test_default_paths_point_inside_repo():
    cfg = ForecastConfig()
    assert Path(cfg.data_path).is_relative_to(PROJECT_ROOT)
    assert Path(cfg.output_dir).is_relative_to(PROJECT_ROOT)
