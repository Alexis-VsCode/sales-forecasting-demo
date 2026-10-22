# 01 — Inventario técnico y diagnóstico

Documento de la Fase 0 (descubrimiento). Sigue el formato del §10 de las instrucciones del proyecto. Cada hallazgo indica su **evidencia** (archivo, línea o commit) para que se pueda comprobar.

- **Línea base analizada:** commit `81034bc` (2026-10-06, autora `raquelvargas16`), último commit del repositorio original.
- **Evolución:** commits `3ebfe87` (paquete modular), `5304e4f` (resultados reales), `be15fee` (notebook y entrega), `826d6ce` (pruebas, CI y `h2o_demo/`) y `5fb8a60` (documentación).

---

## 1. Inventario técnico

### 1.1 Archivos del repositorio original (`git ls-tree -r 81034bc`)

| Archivo | Contenido real | Observación |
|---|---|---|
| `README.md` | 11 líneas: propósito de la demo y pasos de instalación | Pide `java openjdk version >="27"`. |
| `requirements.txt` | `pandas==3.0.3`, `ipykernel==7.3.0`, `statsmodels==0.14.6`, `numpy==2.4.6`, `scikit-learn==1.9.0`, `h2o==3.46.0.12` | Falta `matplotlib`, que el notebook importa. |
| `.gitignore` | `__pycache__`, `.DS_Store` | No excluye `.venv/` ni salidas. |
| `notebooks/ventas_mensuales_live_coding.ipynb` | Template de la sesión en vivo: carga, agregación, descomposición y celdas vacías `# Sigue el código en vivo` | Agrega con `freq='W'`; `datapath = "../../src/data/"`. |
| `src/modeling/arima_trainer.py` | Firma de `select_arima_order(...)` cuyo cuerpo es `pass` | Stub vacío: devuelve `None`. |
| `src/artifacts/__init__.py` | Archivo vacío (0 bytes) | Paquete sin uso. |
| `src/data/stores_sales_forecasting.csv` | Dataset Superstore, categoría Furniture | Ver 1.3. |
| `h2o_demo/main.py` | `H2OAutoMLWrapper` + entrenamiento AutoML sobre la serie agregada | `split_frame` aleatorio; evalúa sobre los datos de entrenamiento. |
| `h2o_demo/src/eng_sales_forecasting.py` | `preprocess_ts()` | Agrega por semana (`'W'`), rutas relativas al directorio de trabajo, escribe en `data/` sin crearlo. |
| `No & Low Code Tools vs Al Assisted Coding.pdf` | Presentación del taller | Fuente de la reflexión Low-Code vs AI-Assisted. |

**No existían** en el original: pruebas automatizadas, CI, `pyproject.toml`, configuración externa, archivo `LICENSE`, documentación técnica.

### 1.2 Entorno y dependencias verificadas

| Componente | Versión | Fuente de la evidencia |
|---|---|---|
| Python | 3.13.16 | `reports/metrics.json` → `environment.python` |
| pandas | 3.0.3 | `reports/metrics.json` |
| numpy | 2.4.6 | `reports/metrics.json` |
| statsmodels | 0.14.6 | `reports/metrics.json` |
| matplotlib | 3.11.2 | `reports/metrics.json` (añadido a `requirements.txt`) |
| scikit-learn | 1.9.0 | `requirements.txt` (no se usa en el núcleo) |
| ipykernel | 7.3.0 | `requirements.txt` |
| h2o | 3.46.0.12 | `reports/evidence/h2o_smoke.txt` |
| Java | OpenJDK 21.0.12.1 | `reports/evidence/h2o_smoke.txt` (H2O arrancó y se apagó con código de salida 0) |
| pytest / ruff / nbconvert | 9.1.1 / 0.17.1 / 7.17.2 | `requirements-dev.txt`, extra `dev` de `pyproject.toml` |

Todas las dependencias están **fijadas** con `==` (salvo `nbclient` en el extra `dev` de `pyproject.toml`, que no lleva versión; en `requirements-dev.txt` sí está fijada en `0.11.0`).

### 1.3 Datos

| Atributo | Valor |
|---|---|
| Archivo | `src/data/stores_sales_forecasting.csv` (no se modifica) |
| Filas | 2121 transacciones |
| Columnas | 21 (`Row ID`, `Order ID`, `Order Date`, …, `Customer Name`, …, `Sales`, `Quantity`, `Discount`, `Profit`) |
| Categoría | Solo *Furniture* |
| Codificación | latin-1; finales de línea CR |
| Formato de fecha | `%m/%d/%Y` |
| Rango | 2014-01-06 a 2017-12-30 |
| Serie mensual resultante | 48 meses (2014-01-01 a 2017-12-01), `freq='MS'`, sin meses vacíos |
| Datos personales | Contiene `Customer Name` y `Customer ID`. Son datos de muestra del conjunto público *Superstore* (no personas reales identificables). El pipeline solo usa `Order Date` y `Sales`. |

### 1.4 Notebooks, scripts y salidas actuales

| Elemento | Estado actual |
|---|---|
| `notebooks/ventas_mensuales_live_coding.ipynb` | Completo, mensual, 35 celdas de código (32 con salidas). |
| `src/sales_forecasting/` | `config.py`, `data.py`, `split.py`, `baselines.py`, `metrics.py`, `diagnostics.py`, `arima.py`, `pipeline.py`, `cli.py`, `__main__.py`. |
| `src/modeling/arima_trainer.py` | Shim que reexporta `select_arima_order` (contrato original conservado). |
| `configs/forecast.toml` | Parámetros no sensibles del pipeline. |
| `reports/` | `metrics.json`, `metrics.csv`, `arima_grid_search.csv`, `forecast_test.csv`, `forecast_future.csv`, `monthly_sales.csv`, `figures/*.png`, `evidence/h2o_smoke.txt`. |
| `tests/` | 9 módulos de prueba (unitarias e integración). |
| `.github/workflows/ci.yml` | Lint (ruff), formato, pytest, pipeline y ejecución del notebook. |
| `entrega/` | PDF, HTML y ZIP del notebook compilado + `README_ENTREGA.md`. |
| `h2o_demo/smoke_h2o.py` | Prueba de humo de arranque de H2O. |

### 1.5 Licencias

- El upstream **no contiene archivo `LICENSE`** (comprobado en `git ls-tree -r 81034bc`). Sin licencia explícita, los derechos de autor quedan reservados a la autora; el uso en esta entrega es académico, dentro del taller para el que se publicó. Para redistribuir o reutilizar fuera de ese contexto hay que solicitar permiso a la autora.
- El dataset *Superstore* circula públicamente (p. ej., Kaggle); su licencia concreta no está documentada en el repositorio: **PENDIENTE DE EVIDENCIA**.
- H2O-3 se distribuye como edición comunitaria (mensaje en `reports/evidence/h2o_smoke.txt`).

---

## 2. Diagnóstico general

El repositorio original es un **material de clase** pensado para completarse en vivo, no un proyecto reproducible: el notebook tenía celdas vacías, la función de selección de orden era un stub y no había pruebas. Además, tenía dos defectos que contradicen la consigna (agregación semanal y ruta de datos rota) y una dependencia faltante que impedía ejecutar el notebook en un entorno limpio. La evolución conserva el propósito y el contrato original, y añade un paquete modular, configuración, pruebas, CI y documentación.

---

## 3. Hallazgos críticos

| ID | Hallazgo | Evidencia | Impacto | Resolución |
|---|---|---|---|---|
| C-1 | Agregación **semanal** cuando la consigna pide **ventas mensuales** | `81034bc:notebooks/…ipynb`, celda `groupby(pd.Grouper(key='Order Date', freq='W'))`; mismo `freq='W'` en `h2o_demo/src/eng_sales_forecasting.py`; etiqueta `ylabel="Ventas semanales"` | Con datos semanales, `seasonal_order=(0,1,0,12)` modela un ciclo de 12 semanas, que no tiene sentido; el resultado no responde a la consigna. | `freq='MS'` en notebook, `configs/forecast.toml`, `data.aggregate_sales` y `preprocess_ts` (con `freq="W"` disponible para reproducir lo anterior). |
| C-2 | Ruta de datos incorrecta | `datapath = "../../src/data/"` en el template; desde `notebooks/` la ruta correcta es `../src/data/` | `FileNotFoundError` al ejecutar el notebook. | El notebook busca la raíz del repo (`pyproject.toml`) y usa `RAIZ / "src" / "data"`. |
| C-3 | `select_arima_order` vacía | `81034bc:src/modeling/arima_trainer.py` termina en `pass` | Cualquier llamada devuelve `None`. | Implementada en `sales_forecasting/arima.py`; el archivo original reexporta la función (ADR-007). |
| C-4 | `matplotlib` no está en `requirements.txt` | `81034bc:requirements.txt`; el notebook hace `import matplotlib.pyplot as plt` | `ModuleNotFoundError` en un entorno limpio. | Añadido `matplotlib==3.11.2`. |

## 4. Hallazgos medios

| ID | Hallazgo | Evidencia | Resolución / estado |
|---|---|---|---|
| M-1 | README exige Java >= 27 | `81034bc:README.md`, commit "Update README.md to include Java OpenJDK version requirement" | H2O 3.46.0.12 arrancó con OpenJDK 21 (`reports/evidence/h2o_smoke.txt`). Java solo es necesario para la demo opcional de H2O. README actualizado. |
| M-2 | Rutas frágiles en `h2o_demo` | `preprocess_ts(data_path="../../src/data/...")` y `result_path = "data/aggregated_sales.csv"` dependen del directorio de trabajo; `h2o_demo/data/` no existía | Rutas resueltas desde `__file__` y `mkdir(parents=True)` (commit `826d6ce`). |
| M-3 | AutoML evaluado sobre los mismos datos de entrenamiento | `print(aml2.leader.model_performance(data_ts))` en `h2o_demo/main.py` | Documentado como optimista y no comparable; no forma parte del núcleo. |
| M-4 | Partición aleatoria (`split_frame`) en `run_automl` | `h2o_demo/main.py` | Adecuada para datos tabulares i.i.d., no para series de tiempo. Documentado en el docstring. |
| M-5 | Parseo de fechas sin formato explícito | `pd.to_datetime(dataset['Order Date'])` | Se fija `format="%m/%d/%Y"` para evitar ambigüedad día/mes. |
| M-6 | Sin pruebas, CI ni configuración externa | Árbol de `81034bc` | `tests/`, `.github/workflows/ci.yml`, `configs/forecast.toml`. |
| M-7 | `src/artifacts/__init__.py` vacío y sin uso | 0 bytes | Se conserva para no alterar la estructura original; es deuda técnica menor. |
| M-8 | `.gitignore` mínimo | Solo `__pycache__` y `.DS_Store` | Ampliado (`.venv/`, `*.egg-info/`, cachés, `h2o_demo/data/`). |

## 5. Quick wins (aplicados)

1. Cambiar `freq='W'` por `freq='MS'` (una línea; corrige el objetivo de la tarea).
2. Corregir la ruta de datos del notebook.
3. Añadir `matplotlib` a `requirements.txt`.
4. Fijar `format="%m/%d/%Y"` al parsear fechas.
5. Ampliar `.gitignore`.
6. Corregir el requisito de Java en el README con evidencia.

## 6. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Serie corta (48 meses; 36 de entrenamiento) | Alta (es un dato) | Estimaciones inestables; diferencias de AIC pequeñas | Comparar con baselines; reportar con cautela. |
| Un solo corte temporal de validación | Alta | Métricas sensibles a un año atípico | Trabajo futuro: validación *rolling origin*. |
| Incompatibilidad de versiones fijadas en otros sistemas (Windows, Python < 3.13) | Media | Fallo de instalación | `requires-python = ">=3.13"`; manual con pasos por sistema. |
| H2O requiere Java y descarga de datos externos en el ejemplo `powerplant` | Media | La demo opcional falla sin Java o sin internet | H2O fuera del núcleo (ADR-005). |
| Entrega posterior al cierre de la plataforma (21-oct-2026 23:59) | Alta | Penalización o rechazo | Coordinar con la docente (decisión del estudiante). |
| Alucinaciones del asistente de IA | Media | Código o conclusiones incorrectas | Toda cifra se verifica contra la ejecución; pruebas automatizadas. |

## 7. Incompatibilidades detectadas

- `seasonal_order=(0,1,0,12)` con datos semanales (C-1).
- Requisito Java >= 27 frente al Java disponible (M-1): no se requiere en la práctica.
- pandas 3: las columnas de texto tienen dtype `str`. El notebook actual describe por separado las columnas numéricas (`describe()`) y las de texto (`describe(include="str")`), en lugar del `describe(include='all')` del template.

## 8. Arquitectura objetivo y plan

Ver `docs/02-arquitectura.md` (diagrama y ADR). El plan aplicado fue:

1. Fase 0 — inventario (este documento).
2. Fase 1 — paquete `sales_forecasting` con pipeline y baselines (`3ebfe87`).
3. Fase 2 — resultados reales del pipeline (`5304e4f`).
4. Fase 3 — notebook mensual completo, correcciones de `h2o_demo`, pruebas, CI y entrega compilada (`be15fee`, `826d6ce`).
5. Fase 4 — documentación (`docs/`, `README.md`; `5fb8a60`) y validaciones (`docs/05-validaciones-evidencias.md`).

## 9. Deuda técnica remanente

- `src/artifacts/` vacío.
- `h2o_demo/main.py` mantiene el diseño original (sin configuración ni partición temporal); no es comparable con el pipeline ARIMA.
- No hay validación cruzada temporal ni modelos alternativos (ETS, regresión).
- Licencia del upstream sin definir.
