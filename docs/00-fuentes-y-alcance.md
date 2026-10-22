# 00 — Fuentes y alcance

Este documento registra qué fuentes se revisaron para preparar la entrega, cuáles **no** se pudieron revisar y qué queda pendiente de definir. Su propósito es que cualquier lector (docente o evaluador) sepa en qué evidencia se apoya cada afirmación del proyecto.

## 1. Actividad evaluada

| Campo | Valor (según captura de la plataforma UCG Casa Grande) |
|---|---|
| Actividad | **S1-Notebook: Modelo ARIMA para predicción de ventas mensuales** |
| Taller | *No & Low Code Tools vs AI Assisted Coding* — Mtr. Raquel Vargas (maestría) |
| Apertura | jueves, 8 de octubre de 2026, 00:00 |
| Cierre | miércoles, 21 de octubre de 2026, 23:59 |
| Objetivo | "Utilizar GitHub Copilot Chat en el desarrollo de un modelo ARIMA para hacer forecast de una serie de tiempo de ventas mensuales." |
| Instrucciones | "Seguir los pasos dados durante la sesión de código en vivo para crear el notebook y subir a la plataforma." |
| Recomendaciones | "Subir el notebook compilado." |
| Formatos permitidos | **PDF** o **ZIP** |
| Estado en la captura | Intento 1, "Todavía no se han realizado envíos", "Sin calificar", 1 hora 43 minutos restantes |

> Observación de plazos: la captura muestra el cierre el **21-oct-2026 23:59**. Este repositorio se preparó el 22-oct-2026 (fecha de los commits `3ebfe87` y `5304e4f`). Si la plataforma ya no admite envíos, el estudiante debe gestionar con la docente una entrega tardía. **PENDIENTE DE CONFIRMACIÓN** por el estudiante.

## 2. Fuentes revisadas

| # | Fuente | Ubicación | Uso en la entrega |
|---|---|---|---|
| 1 | Captura de la consigna en la plataforma | Imagen adjunta por el estudiante (`47da402d-image.jpg`) | Objetivo, instrucciones, formatos y fechas (sección 1). |
| 2 | Presentación del taller | `No & Low Code Tools vs Al Assisted Coding.pdf` (raíz del repo) | Agenda, pros/contras Low/No-Code y AI-Assisted, requisitos de la práctica (VS Code, Python >= 3.13, Copilot Chat), referencias. |
| 3 | Instrucciones del proyecto (`CLAUDE.md` del estudiante) | Archivo adjunto | Lista de entregables (§7), criterios de aceptación (§9), formato de reportes (§10), definición de terminado (§14). |
| 4 | Repositorio upstream | https://github.com/raquelvargas16/sales-forecasting-demo — historial local hasta `81034bc` (2026-10-06) | Código base: notebook template, `src/modeling/arima_trainer.py` (stub), `h2o_demo/`, `requirements.txt`, CSV. |
| 5 | Historial Git local | `git log` (21 commits; 19 de la autora original, 2 de la evolución) | Trazabilidad de cambios. |
| 6 | Código y resultados de la evolución | `src/sales_forecasting/`, `configs/forecast.toml`, `reports/metrics.json`, `reports/metrics.csv`, `reports/arima_grid_search.csv` | Todas las cifras de la documentación. |
| 7 | Notebook ejecutado | `notebooks/ventas_mensuales_live_coding.ipynb` (35 celdas de código, 32 con salidas) | Cifras exploratorias complementarias (se citan indicando que provienen del notebook). |
| 8 | Evidencia de H2O | `reports/evidence/h2o_smoke.txt` | Compatibilidad H2O 3.46.0.12 con OpenJDK 21. |
| 9 | Documentación pública de bibliotecas | statsmodels, pandas, H2O | Semántica de `ARIMA`, `adfuller`, `acorr_ljungbox`, `pd.Grouper`. |

## 3. Fuentes NO revisadas (limitaciones)

| Fuente | Estado | Motivo / acción |
|---|---|---|
| Conversación de ChatGPT de referencia: https://chatgpt.com/share/6ad98338-db00-83e9-b76c-a839f0d67df8 | **NO REVISADA** | No es accesible desde el entorno de ejecución. No se afirma conocer su contenido; ninguna decisión del proyecto se basa en ella. Si el estudiante quiere incorporarla, debe exportarla (texto o PDF) y agregarla al repositorio o al contexto. |
| `sales-forecasting-maestria-prototipo.zip` | **PENDIENTE DE EVIDENCIA** | El archivo no está disponible en el entorno. No se comparó con este repositorio ni se asume que su código esté en GitHub. |
| `sales-forecasting-maestria-v0.2.zip` | **PENDIENTE DE EVIDENCIA** | Igual que el anterior. Nota: la versión del paquete actual (`0.2.0` en `pyproject.toml`) es una numeración propia de esta evolución y **no** implica relación con ese ZIP. |
| Repositorio de entrega https://github.com/Alexis-VsCode/sales-forecasting-demo | **NO VERIFICADO** en este documento | La existencia del fork, permisos, rama remota, PR y CI se registran en `docs/05-validaciones-evidencias.md` y `docs/07-trazabilidad-requisitos.md`. |
| Rúbrica de evaluación de la actividad | **PENDIENTE DE EVIDENCIA** | La captura no muestra rúbrica. Se priorizan objetivo, instrucciones y formato visibles. |
| Grabación o guion de la sesión de código en vivo | **PENDIENTE DE EVIDENCIA** | Solo se dispone del template del notebook con celdas `# Sigue el código en vivo`. El contenido de esas celdas se reconstruyó a partir de los títulos de sección (ADF, descomposición, Ljung-Box, ACF/PACF, ARIMA, métricas, residuos). |

## 4. Elementos pendientes de definición

- **"Gobernanza ISSPOL"**: el estudiante la mencionó, pero no se recibió ningún documento ni requisito al respecto. **PENDIENTE DE DEFINICIÓN con el estudiante.** Este repositorio no incluye contenido sobre ISSPOL. Lo único documentado es una gobernanza básica del uso de IA y de datos, aplicable a esta tarea (ver `docs/08-informe-final.md`, sección 6).
- **Datos del estudiante** (nombre completo, paralelo, fecha de entrega) para la portada del informe y del notebook: deben completarse a mano.

## 5. Alcance

**Dentro del alcance**

- Notebook mensual ARIMA/SARIMA ejecutable y compilado (PDF/ZIP en `entrega/`).
- Paquete Python reproducible (`src/sales_forecasting/`), configuración TOML, CLI, pruebas y CI.
- Comparación con baselines (naive, seasonal naive, media móvil) mediante MAE, RMSE, sMAPE y WAPE sobre un hold-out temporal.
- Documentación académica (`docs/`, `README.md`).
- Verificación de que la demo de H2O arranca con el Java instalado (sin ejecutar AutoML como parte del núcleo).

**Fuera del alcance**

- Despliegue, API, frontend, Docker o servicios en la nube (no los pide la consigna).
- Modificación del dataset original.
- Uso de datos personales reales o de fuentes no públicas.
- Contenido sobre ISSPOL mientras no se defina.
