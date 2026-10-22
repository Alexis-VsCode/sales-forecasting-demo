# Entrega S1-Notebook: Modelo ARIMA para predicción de ventas mensuales

Taller *No & Low Code Tools vs AI Assisted Coding*, Mtr. Raquel Vargas (Maestría, UCG Casa Grande).

## Contenido del ZIP

| Archivo | Descripción |
|---|---|
| `S1_Notebook_ARIMA_ventas_mensuales.pdf` | Notebook ejecutado, exportado a PDF (entregable principal). |
| `S1_Notebook_ARIMA_ventas_mensuales.html` | El mismo notebook ejecutado, en HTML. |
| `notebooks/ventas_mensuales_live_coding.ipynb` | Notebook fuente, con todas las salidas. |
| `src/sales_forecasting/` | Paquete con la carga de datos, partición temporal, baselines, métricas, diagnósticos y ARIMA. |
| `src/modeling/arima_trainer.py` | Módulo original del taller (`select_arima_order`). |
| `src/data/stores_sales_forecasting.csv` | Datos originales (Superstore, Furniture), sin modificar. |
| `configs/forecast.toml`, `pyproject.toml`, `requirements.txt`, `README.md` | Configuración y dependencias del proyecto. |

## Cómo ejecutar

Requisito: Python 3.13. Los comandos se ejecutan desde la carpeta raíz del ZIP descomprimido.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt matplotlib jupyter

# Opción A: abrir notebooks/ventas_mensuales_live_coding.ipynb en VS Code o Jupyter y ejecutar "Run All".
# Opción B: ejecutar el notebook completo desde la terminal:
cd notebooks
jupyter nbconvert --to notebook --execute --inplace ventas_mensuales_live_coding.ipynb --ExecutePreprocessor.timeout=600
```

El notebook busca hacia arriba la carpeta que contiene `pyproject.toml` y agrega `src/` a `sys.path`, así que no hace falta instalar el paquete. Para usar también la línea de comandos del paquete:

```bash
pip install -e .
python -m sales_forecasting --config configs/forecast.toml --output-dir reports
```

### Cómo se generaron el HTML y el PDF

```bash
jupyter nbconvert --to html notebooks/ventas_mensuales_live_coding.ipynb --output-dir . --output S1_Notebook_ARIMA_ventas_mensuales
# Se añadió CSS de impresión (pre-wrap, tamaño A4) al HTML y luego se imprimió con Chromium sin interfaz:
chromium --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=S1_Notebook_ARIMA_ventas_mensuales.pdf file://$PWD/S1_Notebook_ARIMA_ventas_mensuales.html
```

## Notas

- La serie se agrega por **mes** (`freq='MS'`). El template original usaba `freq='W'` (semanal) y la ruta `../../src/data/`; ambos defectos están corregidos.
- El modelo se elige **solo con el entrenamiento** (2014-2016). El conjunto de prueba (2017) se usa únicamente para evaluar.
- Todas las cifras del notebook provienen de su ejecución. Con estos datos, el SARIMA de la sesión en vivo **no supera** al baseline *seasonal naive*, y así se informa.
- Se usó asistencia de IA: GitHub Copilot Chat en la sesión en vivo y un asistente de código de IA en la versión final. Sus propuestas se verificaron contra las salidas reales del código.
