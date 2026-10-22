# 07 — Trazabilidad de requisitos

Vincula cada requisito con los archivos que lo cubren, la evidencia disponible y su estado.

**Estados:** `COMPLETADO` (implementado y con evidencia revisada) · `PARCIAL` (implementado en parte o con evidencia incompleta) · `BLOQUEADO` (depende de algo no disponible) · `NO VERIFICADO` (implementado o previsto, pero su ejecución aún no se ha comprobado en este documento).

> Estado de este documento: actualizado tras la ronda final de validaciones del 2026-10-22 (evidencia en `docs/05-validaciones-evidencias.md`). Siguen `NO VERIFICADO` solo los puntos que dependen de GitHub (push, PR, CI) o de un entorno Windows.

## 1. Consigna de la plataforma (S1-Notebook)

| ID | Requisito | Archivo(s) | Evidencia | Estado |
|---|---|---|---|---|
| P-1 | Modelo ARIMA para pronóstico de una serie de **ventas mensuales** | `notebooks/ventas_mensuales_live_coding.ipynb`, `src/sales_forecasting/arima.py` | `reports/metrics.json`: `freq` = `MS`, 48 periodos, mejor orden (0, 1, 0)×(0, 1, 0, 12), AIC 467.64 | COMPLETADO |
| P-2 | Utilizar GitHub Copilot Chat en el desarrollo | Notebook (celda de presentación), `docs/08-informe-final.md` §6 | Declaración del estudiante; no hay registro automático del uso de Copilot en el repositorio | PARCIAL (autodeclarado) |
| P-3 | Seguir los pasos de la sesión en vivo | Notebook: secciones ADF, descomposición, Ljung-Box, ACF/PACF, ARIMA, métricas y residuos, en el orden del template | Comparación de secciones con `81034bc:notebooks/ventas_mensuales_live_coding.ipynb` | COMPLETADO |
| P-4 | Subir el notebook **compilado** | `entrega/S1_Notebook_ARIMA_ventas_mensuales.pdf`, `.html` | `pdfinfo`: 23 páginas A4, 1574484 bytes; notebook ejecutado con 0 errores; texto verificado con `pdftotext` (docs/05 §5–6). Falta el nombre del estudiante en la portada | COMPLETADO (pendiente: nombre del estudiante) |
| P-5 | Formato PDF o ZIP | `entrega/S1_Notebook_ARIMA_ventas_mensuales.pdf`, `entrega/S1_Notebook_ARIMA_ventas_mensuales.zip` | `unzip -l`: 28 entradas, sin `.venv` ni `__pycache__`; el notebook del ZIP se ejecutó con éxito desde una copia descomprimida (docs/05 §7) | COMPLETADO |
| P-6 | Envío antes del cierre (21-oct-2026 23:59) | Plataforma UCG | Captura: "Todavía no se han realizado envíos"; el trabajo se preparó el 22-oct-2026 | BLOQUEADO (depende del estudiante y de la docente) |

## 2. Entregables del proyecto (CLAUDE.md §7)

| ID | Requisito | Archivo(s) | Evidencia | Estado |
|---|---|---|---|---|
| E-1 | `README.md` profesional (objetivo, arquitectura, requisitos, instalación, ejecución, pruebas, resultados reales, troubleshooting, origen y licencia) | `README.md` | Secciones presentes; cifras tomadas de `reports/metrics.json` | COMPLETADO |
| E-2 | `docs/02-arquitectura.md` con Mermaid y ADR | `docs/02-arquitectura.md` | 2 diagramas Mermaid; ADR-001 a ADR-007 | COMPLETADO |
| E-3 | `docs/03-manual-instalacion-ejecucion.md` | `docs/03-manual-instalacion-ejecucion.md` | Comandos PowerShell y Linux/macOS, troubleshooting | COMPLETADO (redacción); instalación limpia en Windows NO VERIFICADA |
| E-4 | `docs/04-metodologia-pronostico.md` | `docs/04-metodologia-pronostico.md` | Dataset, split 36/12, baselines, fórmulas, resultados | COMPLETADO |
| E-5 | `docs/05-validaciones-evidencias.md` | `docs/05-validaciones-evidencias.md` | Comandos y salidas reales de pytest, ruff, pipeline, nbconvert, pdfinfo, unzip y H2O | COMPLETADO |
| E-6 | `docs/06-guia-presentacion.md` | `docs/06-guia-presentacion.md` | Guion 10 min, 14 preguntas, reflexión del taller | COMPLETADO |
| E-7 | `docs/07-trazabilidad-requisitos.md` | Este documento | Estados actualizados con la evidencia de docs/05 | COMPLETADO |
| E-8 | Código modular | `src/sales_forecasting/*.py`, `src/modeling/arima_trainer.py` | Commit `3ebfe87` | COMPLETADO |
| E-9 | Pruebas automatizadas | `tests/` (9 módulos) | `127 passed, 3 xfailed` (docs/05 §2); los 3 `xfail` documentan 2 bugs conocidos sin corregir | COMPLETADO |
| E-10 | CI de GitHub Actions | `.github/workflows/ci.yml` | Archivo presente; sus comandos pasan en local (docs/05 §2–5); ninguna ejecución en GitHub observada | NO VERIFICADO (en GitHub, pendiente tras el push) |
| E-11 | Informe académico final en Markdown, listo para PDF | `docs/08-informe-final.md` | Redactado; conversión a PDF pendiente | PARCIAL |
| E-12 | Inventario técnico | `docs/01-inventario-tecnico.md` | Hallazgos con evidencia de commits y archivos | COMPLETADO |
| E-13 | Fuentes y alcance (limitaciones de la conversación de ChatGPT y de los ZIP) | `docs/00-fuentes-y-alcance.md` | Conversación no accesible; ZIP no disponibles | COMPLETADO (registro); revisión de esas fuentes BLOQUEADA |

## 3. Criterios de aceptación (CLAUDE.md §9)

| ID | Criterio | Archivo(s) | Evidencia | Estado |
|---|---|---|---|---|
| A-1 | Instalación limpia documentada | `docs/03-…`, `README.md`, `pyproject.toml`, `requirements*.txt` | Documentada para Windows y Linux/macOS | PARCIAL (documentada; instalación limpia NO VERIFICADA en Windows) |
| A-2 | Pipeline ejecutable de extremo a extremo con datos legales | `src/sales_forecasting/pipeline.py`, `cli.py` | Reejecución del CLI en un directorio temporal con `exit=0` (docs/05 §4); dataset público Superstore (licencia exacta PENDIENTE DE EVIDENCIA) | COMPLETADO (licencia del dataset PENDIENTE DE EVIDENCIA) |
| A-3 | Resultados reproducibles y métricas verificables | `reports/metrics.json`, `tests/test_pipeline_integration.py::test_results_match_committed_reports` | La prueba pasa; además, `metrics.json` regenerado es idéntico clave por clave y los CSV coinciden con `cmp` (docs/05 §2 y §4) | COMPLETADO |
| A-4 | Sin secretos, sin rutas absolutas personales, sin fuga temporal | `configs/forecast.toml`, `config.py` (rutas relativas a la raíz), `split.py` | Escaneo `grep` de patrones de secretos: 0 coincidencias; ruta absoluta redactada en la evidencia de H2O; `test_no_temporal_leakage` pasa (docs/05 §9) | COMPLETADO (escaneo por patrones, no una herramienta dedicada) |
| A-5 | Pruebas y lint ejecutados, con fallos reportados | `tests/`, `pyproject.toml` (ruff) | pytest: 127 pasan y 3 `xfail` reportados; ruff check y format sin errores (docs/05 §2–3) | COMPLETADO |
| A-6 | Documentación alineada con el comportamiento real | `docs/`, `README.md` | Cifras contrastadas automáticamente con `reports/`, las salidas del notebook y la evidencia; 4 afirmaciones corregidas (docs/05 §9) | COMPLETADO |
| A-7 | Demostración comprensible | `docs/06-guia-presentacion.md` | Guion y plan B | COMPLETADO |

## 4. Definición de terminado (CLAUDE.md §14)

| ID | Condición | Evidencia | Estado |
|---|---|---|---|
| T-1 | Código en la rama remota (`feat/maestria-sales-forecasting` en `Alexis-VsCode/sales-forecasting-demo`) | Rama local de trabajo: `ccr-4cf3b734-xo4ifd`; no se ha observado push de `feat/maestria-sales-forecasting` | NO VERIFICADO (pendiente) |
| T-2 | Pull Request abierto hacia `main` | — | NO VERIFICADO (pendiente) |
| T-3 | Instrucciones reproducibles | `docs/03-manual-instalacion-ejecucion.md`, `README.md` | COMPLETADO |
| T-4 | Pruebas verificadas | `127 passed, 3 xfailed` en local (docs/05 §2); CI en GitHub pendiente | COMPLETADO en local; CI en GitHub NO VERIFICADO |
| T-5 | Resultados sustentados | `reports/metrics.json`, `reports/arima_grid_search.csv`, notebook ejecutado | COMPLETADO |
| T-6 | Documentación académica alineada con la consigna | `docs/04-…`, `docs/08-informe-final.md` | COMPLETADO |
| T-7 | Fork verificado y permisos de escritura | `git remote -v`: `origin` = https://github.com/Alexis-VsCode/sales-forecasting-demo; permisos de escritura no comprobados | NO VERIFICADO (pendiente del push) |

## 5. Requisitos pendientes de definición

| Requisito | Estado |
|---|---|
| Gobernanza ISSPOL | PENDIENTE DE DEFINICIÓN con el estudiante (no hay contenido en el repositorio) |
| Datos de portada (nombre, curso, fecha) | Por completar por el estudiante |
| Licencia del upstream | Sin `LICENSE`; uso académico; solicitar permiso para redistribuir |
| Bugs conocidos del paquete (`validate_sales` acepta fechas vacías; `temporal_train_test_split` usa `assert`) | Documentados como `xfail(strict=True)`; decidir si se corrigen (y quitar los `xfail`) |
