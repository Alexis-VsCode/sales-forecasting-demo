# 05 — Validaciones y evidencias

Este documento recoge los comandos que se ejecutaron de verdad para validar el proyecto y sus salidas, recortadas solo donde se indica con `…`. No se incluye ninguna salida inventada ni resumida de memoria.

- **Fecha de la verificación:** 2026-10-22 (UTC), entre las 04:01 y las 04:11.
- **Código verificado:** rama local `ccr-4cf3b734-xo4ifd`. Primera pasada sobre `5fb8a60`; pytest, ruff, pipeline y ZIP se repitieron después de `10db0fd` (corrección de `data.py` y `split.py`).
- **Entorno:** contenedor Linux de un solo usuario, con entorno virtual `.venv` y el paquete instalado en modo editable (`pip install -e .`). Todos los comandos se lanzan desde la raíz del repositorio con `.venv` activado.
- **Ejecución de cada comando:** una sola vez, salvo que se indique lo contrario.

## Resumen

| # | Verificación | Resultado |
|---|---|---|
| 1 | Versiones de Python, Java y bibliotecas | PASS |
| 2 | `pytest` | PASS: 130 pasan (los 2 bugs detectados se corrigieron en `10db0fd`) |
| 3 | `ruff check` y `ruff format --check` | PASS |
| 4 | Pipeline por CLI en un directorio temporal, comparado con `reports/` | PASS: `metrics.json`, `arima_grid_search.csv` y `forecast_future.csv` idénticos |
| 5 | Ejecución del notebook con nbconvert | PASS: 0 errores y 35 de 35 celdas de código ejecutadas |
| 6 | PDF de entrega (`pdfinfo`) | PASS: 23 páginas A4 |
| 7 | ZIP de entrega (`unzip -l`) y ejecución del notebook desde el ZIP | PASS: 28 entradas, sin `.venv` ni `__pycache__` |
| 8 | Prueba de humo de H2O con Java 21 | PASS: evidencia de la ejecución del 2026-10-22 a las 03:44 UTC |
| 9 | Escaneo de secretos y rutas absolutas | PASS, tras redactar una ruta en la evidencia de H2O |
| 10 | CI en GitHub Actions | **NO VERIFICADO**: el workflow aún no se ha ejecutado en GitHub y se revisará tras el push |

## 1. Versiones

```text
$ python --version
Python 3.13.16

$ java -version
openjdk version "21.0.12.1" 2026-08-18
OpenJDK Runtime Environment (build 21.0.12.1+1-1-24.04.4-Ubuntu)
OpenJDK 64-Bit Server VM (build 21.0.12.1+1-1-24.04.4-Ubuntu, mixed mode, sharing)

$ pip list   # filtrado a las dependencias del proyecto
h2o                       3.46.0.12
ipykernel                 7.3.0
matplotlib                3.11.2
nbclient                  0.11.0
nbconvert                 7.17.2
numpy                     2.4.6
pandas                    3.0.3
pytest                    9.1.1
ruff                      0.17.1
sales-forecasting         0.2.0
scikit-learn              1.9.0
statsmodels               0.14.6
```

La salida de `java -version` también imprime una línea `Picked up JAVA_TOOL_OPTIONS: …`. La genera el proxy del entorno de ejecución, no el proyecto, y se omite aquí.

## 2. Pruebas (pytest)

```text
$ pytest -q ; echo "exit=$?"
........................................................................ [ 55%]
..........................................................               [100%]
exit=0

$ pytest -o addopts="" -q
..........................................................               [100%]
130 passed in 7.01s

$ pytest -o addopts="" -q -m "not integration"
121 passed, 9 deselected in 2.65s

$ pytest -o addopts="" -q -rA | grep -E "empty_dates|duplicated_timestamp"
PASSED tests/test_data.py::test_empty_dates_are_rejected[None]
PASSED tests/test_data.py::test_empty_dates_are_rejected[]
PASSED tests/test_split.py::test_duplicated_timestamp_at_boundary_raises_value_error
```

`pyproject.toml` ya define `addopts = "-q"`, así que `pytest -q` no imprime la línea de resumen. Para obtener los recuentos se usa `-o addopts=""`.

**Bugs corregidos durante la verificación (commit `10db0fd`).** En una primera pasada (sobre `5fb8a60`) la suite dio `127 passed, 3 xfailed`: tres `xfail(strict=True)` documentaban dos defectos reales del paquete.

- `validate_sales` aceptaba fechas vacías (`None`, `''`) y `aggregate_sales` descartaba esas ventas en silencio. Ahora lanza `DataValidationError`.
- `temporal_train_test_split` validaba el solapamiento con `assert`. Ahora lanza `ValueError` con fechas duplicadas en el borde train/test.

Tras la corrección se quitaron los `xfail` y las tres pruebas pasan. La corrección no cambia ningún resultado: el pipeline vuelve a generar `reports/` idéntico (sección 4).

## 3. Lint y formato (ruff)

```text
$ ruff check src tests
All checks passed!

$ ruff format --check src tests
23 files already formatted
```

## 4. Pipeline reproducible

```text
$ python -m sales_forecasting --config configs/forecast.toml --output-dir <tmp>/verif-reports
… INFO sales_forecasting.data: Datos validados: 2121 filas, 2014-01-06 a 2017-12-30
… INFO sales_forecasting.pipeline: Serie agregada (MS): 48 periodos
… INFO sales_forecasting.pipeline: Mejor orden ARIMA (0, 1, 0) x (0, 1, 0, 12)
… INFO sales_forecasting.pipeline: Resultados guardados en <tmp>/verif-reports
Mejor modelo: SARIMA(0, 1, 0)x(0, 1, 0, 12)
                                    MAE      RMSE  sMAPE    WAPE
modelo
Seasonal naive                  3747.03   4473.38  25.70   20.88
SARIMA(0, 1, 0)x(0, 1, 0, 12)  12219.08  12939.46  59.20   68.08
Moving average (3)             11688.95  13105.84  59.59   65.12
Naive                          18792.78  21085.77  76.79  104.70
Resultados en: <tmp>/verif-reports
exit=0

$ ls <tmp>/verif-reports
arima_grid_search.csv  figures  forecast_future.csv  forecast_test.csv  metrics.csv  metrics.json  monthly_sales.csv
```

**Comparación con los resultados versionados en `reports/`:**

- **`metrics.json`:** un script recorrió los dos JSON clave por clave, contando también las claves de `environment`.

  ```text
  keys 54 54 diffs: []
  ```

  Las 54 claves coinciden. Los valores son idénticos, incluidas las versiones del entorno.
- **CSV:**

  ```text
  $ cmp <tmp>/verif-reports/forecast_future.csv reports/forecast_future.csv && echo forecast_same
  forecast_same
  $ cmp <tmp>/verif-reports/arima_grid_search.csv reports/arima_grid_search.csv && echo grid_same
  grid_same
  ```

- **Repetición tras `10db0fd`:** el pipeline se ejecutó de nuevo con el código corregido en otro directorio temporal (`exit=0`). Los 6 archivos (`metrics.json`, `metrics.csv`, `arima_grid_search.csv`, `forecast_test.csv`, `forecast_future.csv` y `monthly_sales.csv`) resultaron idénticos a los de `reports/` según `cmp`.
- **Directorio de trabajo:** al terminar, `git status --short reports/ src/ configs/` no mostró cambios. El pipeline y las pruebas no modifican `reports/`, el CSV ni la configuración.

## 5. Ejecución del notebook (nbconvert)

```text
$ cd notebooks
$ jupyter nbconvert --to notebook --execute --inplace ventas_mensuales_live_coding.ipynb \
    --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.kernel_name=python3
[NbConvertApp] Converting notebook ventas_mensuales_live_coding.ipynb to notebook
[IPKernelApp] WARNING | Kernel is running over TCP without encryption. …
[NbConvertApp] Writing 810919 bytes to ventas_mensuales_live_coding.ipynb
EXIT=0 tiempo=16s
```

El aviso `Kernel is running over TCP without encryption` es del kernel local de Jupyter y no afecta a los resultados.

**Inspección del `.ipynb` resultante** (se parseó como JSON con un script):

```text
celdas 70 código 35 errores 0 sin_ejecutar 0 imágenes 8
ruta /home/user presente: False
idénticas por celda (ignorando la hora de statsmodels): True
```

El notebook se volvió a ejecutar después de corregir un texto de interpretación (ver la sección 9). Sus salidas coinciden celda por celda con la ejecución anterior. La única diferencia es la línea `Time:` de los resúmenes de statsmodels.

## 6. PDF de entrega

```text
$ pdfinfo entrega/S1_Notebook_ARIMA_ventas_mensuales.pdf
Title:           ventas_mensuales_live_coding
Creator:         Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/141.0.0.0 Safari/537.36
Producer:        Skia/PDF m141
…
Pages:           23
Encrypted:       no
Page size:       594.96 x 841.92 pts (A4)
File size:       1574484 bytes
```

**Cómo se generó:** el HTML de `nbconvert` se imprimió a PDF con Chromium *headless*. El procedimiento completo está en `entrega/README_ENTREGA.md`.

**Comprobaciones con `pdftotext`:**

- El texto corregido de la sección 9 aparece en el PDF.
- La portada muestra `Estudiante: (completar)`, a la espera del nombre.

## 7. ZIP de entrega

```text
$ unzip -l entrega/S1_Notebook_ARIMA_ventas_mensuales.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/
      819  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/src/sales_forecasting/split.py
     2802  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/src/sales_forecasting/data.py
        …  (otros 9 archivos .py de src/sales_forecasting/)
   494695  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/src/data/stores_sales_forecasting.csv
      485  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/src/modeling/arima_trainer.py
      118  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/requirements.txt
     9017  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/README.md
     2991  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/README_ENTREGA.md
   811232  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/notebooks/ventas_mensuales_live_coding.ipynb
      731  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/configs/forecast.toml
      992  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/pyproject.toml
  1142232  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/S1_Notebook_ARIMA_ventas_mensuales.html
  1574484  2026-10-22 04:10   S1_Notebook_ARIMA_ventas_mensuales/S1_Notebook_ARIMA_ventas_mensuales.pdf
---------                     -------
  4060116                     28 files

$ unzip -l entrega/S1_Notebook_ARIMA_ventas_mensuales.zip | grep -cE '\.venv|__pycache__|\.pyc'
0
```

**Comprobaciones adicionales:**

- **Correspondencia con el repositorio:** el `.ipynb` y el `README.md` del ZIP son idénticos byte a byte (`cmp`) a los del repositorio. El ZIP se regeneró dos veces en esta verificación: la primera porque contenía el `README.md` original, que pedía Java >= 27, y la segunda para incluir el `src/` corregido en `10db0fd`. Tras la segunda, `diff -rq` entre `src/sales_forecasting` del ZIP y del repositorio no muestra diferencias.
- **Ejecución desde el ZIP:** se descomprimió el ZIP en un directorio temporal y se ejecutó su notebook con nbconvert (tras la segunda regeneración). Terminó con `EXIT=0`, 0 errores y reprodujo las mismas cifras, por ejemplo RMSE 12939.46 del SARIMA y 4473.38 del *seasonal naive*.

## 8. Prueba de humo de H2O (Java 21)

**Fuente:** [`reports/evidence/h2o_smoke.txt`](../reports/evidence/h2o_smoke.txt).

- **Ejecución:** la evidencia corresponde a la ejecución de `timeout 240 python h2o_demo/smoke_h2o.py` del 2026-10-22 a las 03:44:31 UTC. Durante esta verificación no se volvió a lanzar H2O.
- **Redacción:** en esta revisión se sustituyó la ruta absoluta del entorno por `<repo>`; el resto del archivo no se modificó.

```text
python: 3.13.16
h2o (paquete Python): 3.46.0.12
java: openjdk version "21.0.12.1" 2026-08-18
…
H2O_cluster_version:        3.46.0.12
H2O_cluster_status:         locked, healthy
…
h2o.cluster().version: 3.46.0.12
tiempo de arranque (s): 6.5
H2O session _sid_b2eb closed.
clúster apagado correctamente

# código de salida del proceso python: 0
```

**Qué demuestra:** H2O 3.46.0.12 arranca y se apaga con OpenJDK 21. El requisito "Java >= 27" del README original no es necesario.

**Qué no demuestra:** AutoML (`h2o_demo/main.py`) **no** se ejecutó.

## 9. Revisión de veracidad, secretos y rutas

**Cifras con decimales.** Un script extrajo todas las cifras con decimales de `README.md`, `docs/*.md`, `entrega/README_ENTREGA.md` y las celdas Markdown del notebook. Luego buscó cada una en las fuentes de referencia:

- `reports/*.json` y `reports/*.csv`;
- las salidas del notebook ejecutado;
- `reports/evidence/h2o_smoke.txt`;
- los archivos de dependencias.

Solo quedaron sin correspondencia los números de sección (1.1, 4.2, …) y dos cifras escritas con otro formato pero equivalentes: 0.00028 (redondeo de 0.000278) y 8.45e-05.

**Afirmaciones corregidas en esta revisión:**

| Archivo | Antes | Después | Motivo |
|---|---|---|---|
| Notebook (celda de métricas) y `docs/04` §9 | El SARIMA "apenas supera" (o "mejora ligeramente") a la media móvil **y al naive** | Mejora apenas a la media móvil, y solo supera con claridad al naive | RMSE 12939.46 frente a 21085.77 no es una mejora "ligera". Además, la media móvil tiene mejor MAE (11688.95 frente a 12219.08). |
| `docs/03` §8 | AutoML "(~60 s)" | `max_runtime_secs=60`; no se ejecutó en esta verificación | No había ninguna medición de esa duración. |
| `docs/08` §6.1 | "Verificación humana: … decisiones tomadas con criterio propio" | Las cifras salen de la ejecución (este documento); el estudiante debe revisar y asumir las decisiones. El uso de Copilot Chat queda como autodeclarado. | No hay evidencia en el repositorio de quién tomó cada decisión. |
| `docs/08` §6.2 | "No se pegaron secretos en el asistente" | Resultado del escaneo de secretos | La afirmación original no se podía verificar. |
| `reports/evidence/h2o_smoke.txt` | Contenía la ruta absoluta del entorno | Ruta reemplazada por `<repo>`, con una nota | Sin rutas absolutas en archivos versionados. |
| `.gitignore` | No excluía las salidas de la CI | Añadidos `ci-reports/` y `ci-notebooks/` | Evitar que se versionen por error. |

**Escaneo de secretos.** Sobre los 57 archivos versionados o candidatos (sin `.venv`) se buscaron estos patrones con `grep -E`:

- claves de AWS;
- tokens de GitHub;
- claves `sk-…`;
- tokens de Slack;
- claves privadas PEM;
- asignaciones `api_key=`, `password=` y `secret=`.

Resultado: **0 coincidencias**.

**Rutas absolutas.** Antes de esta revisión, el único archivo con la ruta absoluta del entorno era `reports/evidence/h2o_smoke.txt`; tras la redacción indicada arriba no queda ninguno (este documento solo la menciona al describir la comprobación). Ni el `.ipynb` ni el HTML contienen rutas absolutas.

**ISSPOL.** El repositorio no contiene ninguna afirmación sobre ISSPOL. Solo aparece como "PENDIENTE DE DEFINICIÓN" en `docs/00`, `docs/07` y `docs/08`.

## 10. CI en GitHub Actions

- **Validado en local:**
  - `.github/workflows/ci.yml` existe. Define el job `test` (ruff, pytest, pipeline y artifact) y el job `notebook` (nbconvert y artifact).
  - Los comandos del job `test` se ejecutaron en local con resultado PASS (secciones 2 a 4).
  - El comando del job `notebook` es equivalente al de la sección 5.
- **Pendiente:** **NO VERIFICADO** en GitHub. El estado real del workflow (verde o rojo) se comprobará en la pestaña *Actions* después de hacer push de la rama y abrir el Pull Request. Hasta entonces no debe afirmarse que la CI pasa en GitHub.
