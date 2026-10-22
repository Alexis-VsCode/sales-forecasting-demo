# 03 — Manual de instalación y ejecución

Guía paso a paso para instalar, ejecutar y verificar el proyecto en **Windows (PowerShell)** y **Linux/macOS (bash/zsh)**. Todos los comandos se ejecutan desde la **raíz del repositorio** (la carpeta que contiene `pyproject.toml`).

## 0. Requisitos

| Requisito | Versión | ¿Obligatorio? |
|---|---|---|
| Python | **>= 3.13** (verificado con 3.13.16) | Sí |
| Git | cualquiera reciente | Para clonar |
| Visual Studio Code + extensiones *Python*, *Jupyter* y *GitHub Copilot Chat* | — | Para la práctica del taller |
| Java (OpenJDK) | Verificado con **OpenJDK 21** (`reports/evidence/h2o_smoke.txt`) | Solo para la demo opcional de H2O |

> El README original pedía Java >= 27. No es necesario: H2O 3.46.0.12 arrancó correctamente con OpenJDK 21. El núcleo ARIMA no usa Java.

Comprobar versiones:

```powershell
# Windows PowerShell
py --version          # o: python --version
java -version         # solo si usará H2O
```

```bash
# Linux / macOS
python3 --version
java -version         # solo si usará H2O
```

## 1. Obtener el código

```bash
git clone https://github.com/Alexis-VsCode/sales-forecasting-demo.git
cd sales-forecasting-demo
```

(El repositorio original de la docente es https://github.com/raquelvargas16/sales-forecasting-demo.)

## 2. Crear y activar el entorno virtual

**Windows PowerShell**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**Linux / macOS**

```bash
python3.13 -m venv .venv      # o python3 si ya es 3.13
source .venv/bin/activate
python -m pip install --upgrade pip
```

Al activarse, el prompt muestra `(.venv)`.

## 3. Instalar dependencias

Hay dos formas equivalentes; elija una.

**Opción A — requisitos del taller + paquete en modo editable (recomendada para desarrollo):**

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

**Opción B — todo en un paso (incluye pruebas, lint y nbconvert):**

```bash
pip install -r requirements-dev.txt
```

Notas:

- `requirements.txt` incluye `h2o==3.46.0.12` por compatibilidad con el taller. Si solo quiere el núcleo ARIMA: `pip install -e ".[dev]"` (sin H2O).
- Para añadir H2O después: `pip install -e ".[h2o]"`.
- En PowerShell las comillas de `".[dev]"` son necesarias.

## 4. Ejecutar el pipeline de pronóstico

```bash
python -m sales_forecasting --config configs/forecast.toml
```

Opciones:

- `--output-dir DIR`: escribe los resultados en otra carpeta (útil para no sobrescribir `reports/`).
- `-v`: registro detallado (nivel DEBUG).

También se instala el comando `sales-forecast` (equivalente).

Ejemplo sin tocar `reports/`:

```powershell
# Windows
python -m sales_forecasting --config configs/forecast.toml --output-dir salida-local
```

```bash
# Linux / macOS
python -m sales_forecasting --config configs/forecast.toml --output-dir /tmp/salida-local
```

**Salidas** (en `reports/` por defecto):

| Archivo | Contenido |
|---|---|
| `metrics.json` | Resumen: periodos, partición, orden elegido, AIC, ADF, métricas, Ljung-Box y versiones. |
| `metrics.csv` | Métricas por modelo, ordenadas por RMSE. |
| `arima_grid_search.csv` | AIC y BIC de cada orden (p, d, q) probado. |
| `forecast_test.csv` | Real vs. pronósticos de todos los modelos en 2017 (+ IC del SARIMA). |
| `forecast_future.csv` | Pronóstico de 12 meses (2018) con IC 95 %. |
| `monthly_sales.csv` | Serie mensual agregada. |
| `figures/forecast_test.png`, `figures/forecast_future.png` | Gráficos. |

El comando imprime el modelo elegido y la tabla de métricas. Las cifras esperadas están en `docs/04-metodologia-pronostico.md`.

## 5. Ejecutar las pruebas y el lint

```bash
pytest                         # todas las pruebas
pytest -m "not integration"    # solo las unitarias (rápidas)
ruff check src tests           # lint
ruff format --check src tests  # formato
```

Las pruebas de integración ejecutan el pipeline con el CSV real y comparan sus resultados con `reports/metrics.json`.

## 6. Ejecutar el notebook

### 6.1 En Visual Studio Code

1. Abrir la carpeta del repositorio (`File > Open Folder`).
2. Abrir `notebooks/ventas_mensuales_live_coding.ipynb`.
3. Elegir el kernel: botón **Select Kernel** (arriba a la derecha) → *Python Environments* → `.venv`.
4. **Restart** y luego **Run All**.

El notebook localiza la raíz del repo buscando `pyproject.toml` y agrega `src/` a `sys.path`, así que funciona aunque el paquete no esté instalado.

### 6.2 Desde la terminal (nbconvert)

```bash
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebooks/ventas_mensuales_live_coding.ipynb
```

En PowerShell, use una sola línea (o el acento grave `` ` `` en lugar de `\` para continuar líneas):

```powershell
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/ventas_mensuales_live_coding.ipynb
```

Si el kernel `python3` no existe: `python -m ipykernel install --user --name python3`.

## 7. Exportar el notebook compilado (PDF / ZIP)

La consigna acepta **PDF** o **ZIP**. La entrega ya generada está en `entrega/` (ver `entrega/README_ENTREGA.md`).

**a) HTML con nbconvert y PDF desde el navegador (no requiere LaTeX):**

```bash
jupyter nbconvert --to html notebooks/ventas_mensuales_live_coding.ipynb --output-dir entrega --output S1_Notebook_ARIMA_ventas_mensuales
```

Abra el HTML en el navegador y use **Imprimir → Guardar como PDF**. Así se generó el PDF de `entrega/` (con Chromium en modo *headless*; el comando exacto está en `entrega/README_ENTREGA.md`).

**b) Desde VS Code:** en el notebook, menú `...` → **Export** → *HTML* o *PDF* (la exportación a PDF de VS Code requiere una distribución de LaTeX instalada).

**c) `nbconvert --to pdf`:** también requiere LaTeX (TeX Live o MiKTeX). No se usó en esta entrega.

**ZIP:** comprima el PDF, el HTML, el `.ipynb` y la carpeta `src/` (ver la lista de `entrega/README_ENTREGA.md`).

## 8. Demo opcional de H2O AutoML

Requiere Java en el `PATH`.

```bash
pip install -e ".[h2o]"
python h2o_demo/smoke_h2o.py     # arranca y apaga un clúster local de H2O
python h2o_demo/main.py          # AutoML sobre la serie mensual (max_runtime_secs=60; no ejecutado en la verificación de docs/05)
```

Advertencia: `main.py` evalúa el líder de AutoML sobre los mismos datos de entrenamiento, así que su métrica es optimista y **no es comparable** con las métricas de prueba del SARIMA.

## 9. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled` | Política de ejecución de PowerShell | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (o, solo para la sesión: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`). |
| `py` o `python` abre la Microsoft Store (Windows) | Alias de la Store | Instalar Python 3.13 desde python.org y desactivar los "alias de ejecución de aplicaciones". |
| `UnicodeDecodeError` al leer el CSV | El archivo es latin-1, no UTF-8 | Usar `load_sales_csv` o `pd.read_csv(..., encoding="latin-1", encoding_errors="replace")`. No convertir ni guardar de nuevo el CSV. |
| `FileNotFoundError: ../../src/data/...` | Ruta del template original | Usar el notebook actual (ruta resuelta desde la raíz) o `../src/data/` desde `notebooks/`. |
| `ModuleNotFoundError: matplotlib` | Entorno creado con el `requirements.txt` original | `pip install -r requirements.txt` (ya incluye `matplotlib==3.11.2`). |
| `ModuleNotFoundError: sales_forecasting` | Paquete no instalado y ejecución fuera de la raíz | `pip install -e .` desde la raíz. |
| VS Code no muestra `.venv` como kernel | Falta `ipykernel` o el entorno no está seleccionado | `pip install ipykernel==7.3.0`; `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`. |
| `No such kernel named python3` (nbconvert) | Kernel no registrado | `python -m ipykernel install --user --name python3`. |
| Pip falla con `requires a different Python` | Python < 3.13 | Instalar Python 3.13 y recrear `.venv`. |
| H2O: `Cannot find Java` | Java no instalado o fuera del `PATH` | Instalar un OpenJDK (verificado: 21) y comprobar `java -version`. Solo afecta a la demo opcional. |
| H2O se cuelga al arrancar | Puerto 54321 ocupado o poca memoria | Cerrar otras instancias; `h2o.init(max_mem_size="1G")`. |
| `nbconvert --to pdf` falla con `xelatex not found` | No hay LaTeX | Usar la vía HTML → imprimir a PDF (sección 7a). |
| Gráficos no aparecen al ejecutar el CLI | El CLI usa el backend `Agg` (sin pantalla) | Es intencional: las figuras se guardan en `reports/figures/`. |
