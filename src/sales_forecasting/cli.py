"""Interfaz de línea de comandos: ``python -m sales_forecasting --config configs/forecast.toml``."""

from __future__ import annotations

import argparse
import logging
import sys

import matplotlib

matplotlib.use("Agg")

from .config import load_config  # noqa: E402
from .pipeline import run_pipeline, save_outputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pronóstico de ventas mensuales con SARIMA")
    parser.add_argument("--config", default=None, help="Ruta a un archivo TOML de configuración")
    parser.add_argument("--output-dir", default=None, help="Sobrescribe el directorio de salida")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config(args.config)
    if args.output_dir:
        from dataclasses import replace
        from pathlib import Path

        config = replace(config, output_dir=Path(args.output_dir))

    result = run_pipeline(config)
    out = save_outputs(result, config)
    print(f"Mejor modelo: SARIMA{result.best_order}x{result.seasonal_order}")
    print(result.metrics.round(2).to_string())
    print(f"Resultados en: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
