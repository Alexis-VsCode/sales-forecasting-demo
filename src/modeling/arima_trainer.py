"""Módulo original del taller. Se conserva el contrato de ``select_arima_order``;
la implementación vive en ``sales_forecasting.arima`` para no duplicar lógica."""

import sys
from pathlib import Path

try:
    from sales_forecasting.arima import select_arima_order
except ModuleNotFoundError:  # uso sin `pip install -e .`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sales_forecasting.arima import select_arima_order

__all__ = ["select_arima_order"]
