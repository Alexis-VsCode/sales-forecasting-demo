"""Configuración externa (TOML, sin secretos) del pipeline de pronóstico."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ForecastConfig:
    data_path: Path = PROJECT_ROOT / "src" / "data" / "stores_sales_forecasting.csv"
    output_dir: Path = PROJECT_ROOT / "reports"
    date_column: str = "Order Date"
    target_column: str = "Sales"
    date_format: str = "%m/%d/%Y"
    freq: str = "MS"
    test_size: int = 12
    horizon: int = 12
    season_length: int = 12
    moving_average_window: int = 3
    p_values: tuple[int, ...] = (0, 1, 2)
    d_values: tuple[int, ...] = (1,)
    q_values: tuple[int, ...] = (0, 1, 2)
    seasonal_order: tuple[int, int, int, int] = (0, 1, 0, 12)
    ljung_box_lags: tuple[int, ...] = (6, 12)
    alpha: float = 0.05
    seed: int = 42

    def __post_init__(self) -> None:
        if self.test_size <= 0 or self.horizon <= 0:
            raise ValueError("test_size y horizon deben ser enteros positivos")
        if not 0 < self.alpha < 1:
            raise ValueError("alpha debe estar en (0, 1)")
        if len(self.seasonal_order) != 4:
            raise ValueError("seasonal_order debe tener 4 elementos (P, D, Q, s)")


def _resolve(path_value: str | Path, base: Path) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else (base / path).resolve()


def load_config(path: str | Path | None = None) -> ForecastConfig:
    """Carga la configuración desde TOML; rutas relativas se resuelven contra la raíz del repo."""
    if path is None:
        return ForecastConfig()
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)
    data = raw.get("data", {})
    split = raw.get("split", {})
    model = raw.get("model", {})
    diag = raw.get("diagnostics", {})
    kwargs: dict = {}
    if "path" in data:
        kwargs["data_path"] = _resolve(data["path"], PROJECT_ROOT)
    if "output_dir" in raw.get("output", {}):
        kwargs["output_dir"] = _resolve(raw["output"]["output_dir"], PROJECT_ROOT)
    for key in ("date_column", "target_column", "date_format", "freq"):
        if key in data:
            kwargs[key] = data[key]
    for key in ("test_size", "horizon"):
        if key in split:
            kwargs[key] = int(split[key])
    for key in ("season_length", "moving_average_window", "seed"):
        if key in model:
            kwargs[key] = int(model[key])
    for key in ("p_values", "d_values", "q_values"):
        if key in model:
            kwargs[key] = tuple(int(v) for v in model[key])
    if "seasonal_order" in model:
        kwargs["seasonal_order"] = tuple(int(v) for v in model["seasonal_order"])
    if "ljung_box_lags" in diag:
        kwargs["ljung_box_lags"] = tuple(int(v) for v in diag["ljung_box_lags"])
    if "alpha" in diag:
        kwargs["alpha"] = float(diag["alpha"])
    return ForecastConfig(**kwargs)
