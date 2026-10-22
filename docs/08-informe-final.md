---
title: "Modelo ARIMA para predicción de ventas mensuales"
subtitle: "S1-Notebook — Taller No & Low Code Tools vs AI Assisted Coding"
lang: es
---

# Modelo ARIMA para predicción de ventas mensuales

| | |
|---|---|
| **Estudiante** | _(completar)_ |
| **Programa / curso** | _(completar)_ — Maestría, Universidad Casa Grande (UCG) |
| **Taller** | *No & Low Code Tools vs AI Assisted Coding* |
| **Docente** | Mtr. Raquel Vargas |
| **Actividad** | S1-Notebook: Modelo ARIMA para predicción de ventas mensuales |
| **Fecha** | _(completar)_ |
| **Repositorio** | https://github.com/Alexis-VsCode/sales-forecasting-demo (derivado de https://github.com/raquelvargas16/sales-forecasting-demo) |

---

## Resumen

Se desarrolló, con asistencia de IA (GitHub Copilot Chat), un modelo SARIMA para pronosticar las ventas mensuales de la categoría *Furniture* del conjunto de datos Superstore. Las 2121 transacciones se agregaron en una serie de 48 meses (2014-01 a 2017-12). Con una partición temporal de 36 meses de entrenamiento y 12 de prueba, el criterio AIC aplicado solo sobre el entrenamiento seleccionó SARIMA(0, 1, 0)×(0, 1, 0, 12) (AIC 467.64). En la prueba (2017), este modelo obtuvo MAE 12219.08, RMSE 12939.46, sMAPE 59.20 % y WAPE 68.08 %, y **no superó** al baseline *seasonal naive* (MAE 3747.03, RMSE 4473.38, sMAPE 25.70 %, WAPE 20.88 %). El test de Ljung-Box sobre los residuos (p = 0.0386 en el rezago 6 y p = 0.0105 en el rezago 12) indica autocorrelación remanente. Se concluye que la estructura de la sesión en vivo es insuficiente para esta serie y que la comparación con baselines es imprescindible para no adoptar un modelo peor que una regla simple.

**Palabras clave:** series de tiempo, SARIMA, Box-Jenkins, pronóstico de ventas, baselines, asistentes de código con IA.

## 1. Introducción

Pronosticar la demanda mensual permite planificar inventario, compras y personal. Los modelos ARIMA y su extensión estacional SARIMA (Box y Jenkins) son una referencia clásica para series univariadas con tendencia y estacionalidad.

La actividad tiene dos objetivos: (i) construir un modelo ARIMA para una serie de ventas mensuales siguiendo la sesión de código en vivo, y (ii) experimentar con un asistente de programación con IA (GitHub Copilot Chat) en contraste con herramientas Low/No-Code como H2O AutoML, tema central del taller.

El punto de partida fue el repositorio del taller, que contenía un notebook con celdas por completar, un stub vacío de selección de orden ARIMA y una demo de H2O. Al revisarlo se detectaron defectos que afectaban directamente la consigna, entre ellos la agregación semanal de la serie.

## 2. Datos

- **Fuente:** `src/data/stores_sales_forecasting.csv`, subconjunto *Furniture* del conjunto público de demostración Superstore (sin modificar).
- **Volumen:** 2121 transacciones, del 2014-01-06 al 2017-12-30.
- **Variables usadas:** `Order Date` (formato `%m/%d/%Y`) y `Sales`.
- **Preparación:** lectura latin-1; validación de columnas, fechas y ventas (numéricas, no negativas); suma mensual con `freq='MS'`. Resultado: 48 observaciones sin meses vacíos.
- **Corrección del template:** se reemplazó `freq='W'` (semanal) por `freq='MS'` (mensual) y se corrigió la ruta `../../src/data/`, inexistente desde `notebooks/`.

## 3. Metodología

1. **Exploración:** gráfico de la serie, ventas anuales (157192.85 en 2014 y 215387.27 en 2017, según el notebook), descomposición multiplicativa con periodo 12 y ACF/PACF.
2. **Estacionariedad:** ADF (α = 0.05). Sobre el entrenamiento: estadístico −3.8778, p = 0.0022; con diferencia estacional: p = 0.00028. Ambos rechazan la raíz unitaria, aunque el test tiene baja potencia con pocos datos y no evalúa raíces estacionales.
3. **Partición temporal:** entrenamiento 2014-01 a 2016-12 (36 meses), prueba 2017-01 a 2017-12 (12 meses), sin barajar.
4. **Selección del modelo:** rejilla SARIMA(p, 1, q)×(0, 1, 0, 12) con p, q ∈ {0, 1, 2} (9 modelos) sobre el entrenamiento; criterio AIC.
5. **Baselines:** *naive*, *seasonal naive* (s = 12) y media móvil de 3 meses.
6. **Métricas en prueba:** MAE, RMSE, sMAPE y WAPE (fórmulas en `docs/04-metodologia-pronostico.md`).
7. **Diagnóstico:** Ljung-Box sobre los residuos (rezagos 6 y 12), descartando los 13 primeros, afectados por la diferenciación.
8. **Pronóstico futuro:** reentrenamiento con 48 meses y horizonte de 12 meses (2018), con intervalo de confianza del 95 %.

**Herramientas:** Python 3.13.16, pandas 3.0.3, numpy 2.4.6, statsmodels 0.14.6, matplotlib 3.11.2, Visual Studio Code y GitHub Copilot Chat. El código reutilizable está en el paquete `src/sales_forecasting/`, con pruebas automatizadas y configuración en `configs/forecast.toml`.

## 4. Resultados

### 4.1 Selección del orden

El menor AIC correspondió a SARIMA(0, 1, 0)×(0, 1, 0, 12), con AIC = 467.64. El segundo, (1, 1, 1), obtuvo 468.30: una diferencia menor que 1 punto, por lo que se prefirió el modelo más parsimonioso.

### 4.2 Evaluación en el conjunto de prueba (2017)

| Modelo | MAE | RMSE | sMAPE (%) | WAPE (%) |
|---|---|---|---|---|
| **Seasonal naive** | **3747.03** | **4473.38** | **25.70** | **20.88** |
| SARIMA(0, 1, 0)×(0, 1, 0, 12) | 12219.08 | 12939.46 | 59.20 | 68.08 |
| Media móvil (3) | 11688.95 | 13105.84 | 59.59 | 65.12 |
| Naive | 18792.78 | 21085.77 | 76.79 | 104.70 |

Fuente: `reports/metrics.json`, generado con `python -m sales_forecasting --config configs/forecast.toml`.

### 4.3 Diagnóstico de residuos

| Rezago | Q de Ljung-Box | p-valor |
|---|---|---|
| 6 | 13.2957 | 0.0386 |
| 12 | 26.0748 | 0.0105 |

Ambos p-valores son menores que 0.05: los residuos no se comportan como ruido blanco.

### 4.4 Figuras

- `reports/figures/forecast_test.png`: entrenamiento, valores reales de 2017, pronóstico SARIMA con IC 95 % y *seasonal naive*.
- `reports/figures/forecast_future.png`: histórico y pronóstico de 2018.

## 5. Discusión

El resultado principal es que **el modelo de la sesión en vivo no supera al *seasonal naive***: su RMSE es casi el triple. La explicación es estructural. Sin términos AR ni MA y con d = D = 1, el pronóstico equivale a repetir el mismo mes del año anterior y sumarle el último cambio interanual. En la prueba, ese cambio (diciembre de 2016 frente a diciembre de 2015, +13592.90 según el notebook) fue atípico y no se repitió en 2017, de modo que el modelo sobreestimó todo el horizonte.

El diagnóstico de residuos confirma que la especificación está incompleta. En una extensión exploratoria del notebook, al permitir términos estacionales P y Q, el AIC eligió SARIMA(0, 1, 0)×(1, 1, 0, 12) (AIC 465.94), cuyos residuos ya no muestran autocorrelación significativa y cuyo RMSE de prueba baja a 10574.03. Aun así, sigue lejos del *seasonal naive*. Con un único año de prueba y diferencias de AIC pequeñas, estos resultados no deben sobreinterpretarse.

El pronóstico de 2018 del SARIMA reentrenado (total de 152132.29, frente a 215387.27 vendidos en 2017, según el notebook) contradice la tendencia creciente observada y tiene límites inferiores negativos en su intervalo de confianza. No es apto para la toma de decisiones sin mejorar el modelo.

**Limitaciones:** serie corta (48 meses), un único corte de validación, una sola categoría, ausencia de variables exógenas y posible sobrediferenciación.

## 6. Uso de IA asistida y gobernanza básica

### 6.1 Uso de la IA

- **GitHub Copilot Chat** (Visual Studio Code) durante la sesión en vivo: generación de código para pruebas estadísticas, búsqueda en rejilla, métricas y gráficos.
- **Asistente de código de IA** para la versión final: modularización en el paquete `sales_forecasting`, pruebas, CI y documentación.
- **Verificación:** cada cifra del notebook y de este informe proviene de ejecutar el código (comandos y salidas en `docs/05-validaciones-evidencias.md`). Las propuestas de la IA se contrastaron con las salidas reales. Las decisiones metodológicas (frecuencia mensual, partición sin fuga, baselines, lectura de residuos, conclusión) deben ser revisadas y asumidas por el estudiante antes de la entrega.
- El uso de Copilot Chat en la sesión en vivo es una declaración del estudiante: el repositorio no guarda un registro automático de ese uso.

Esto coincide con lo que plantea la presentación del taller: la IA asistida es útil para tests, documentación, *refactoring* y código repetitivo, pero tiene riesgos de alucinación, de exposición de información sensible y de "miopía de arquitectura". En este caso, el template ya tenía decisiones incorrectas (`freq='W'` y una ruta rota) que un asistente sin contexto podía reproducir.

### 6.2 Gobernanza básica de IA y datos

| Aspecto | Práctica aplicada |
|---|---|
| Secretos | No se usan credenciales ni API keys; la configuración (`configs/forecast.toml`) no contiene datos sensibles. Un escaneo con `grep` de patrones de credenciales en el repositorio no encontró coincidencias (`docs/05-validaciones-evidencias.md`). |
| Datos personales | El CSV del Superstore incluye `Customer Name` y `Customer ID`. Es un conjunto público de demostración, con clientes de muestra. El modelo solo usa `Order Date` y `Sales`; no se derivan ni publican datos de clientes. Se recomienda no subir a asistentes de IA columnas identificativas cuando se trabaje con datos reales. |
| Integridad de los datos | El CSV original no se modifica; las transformaciones se hacen en memoria. |
| Trazabilidad | Historial Git, configuración versionada, versiones de bibliotecas registradas en `reports/metrics.json`. |
| Reproducibilidad | Pipeline por línea de comandos y prueba de integración que compara los resultados con `reports/metrics.json`. |
| Transparencia | Se declara el uso de IA y se informa que el modelo no supera al baseline. |
| Atribución y licencia | Se reconoce el repositorio original de la docente, que no incluye licencia explícita; su uso es académico. |

> La "gobernanza ISSPOL" mencionada por el estudiante queda **PENDIENTE DE DEFINICIÓN**; este informe no contiene información sobre esa institución.

## 7. Conclusiones

1. Se construyó y evaluó un modelo SARIMA para ventas **mensuales**, corrigiendo la agregación semanal y la ruta de datos del template.
2. La selección por AIC sobre el entrenamiento eligió SARIMA(0, 1, 0)×(0, 1, 0, 12) (AIC 467.64).
3. En 2017, el *seasonal naive* (RMSE 4473.38) superó al SARIMA (RMSE 12939.46), y los residuos del SARIMA presentan autocorrelación (Ljung-Box p = 0.0386 y 0.0105).
4. Un modelo más complejo no garantiza mejores pronósticos; comparar con referencias simples es indispensable.
5. Los asistentes de IA aceleran el desarrollo, pero la validez metodológica depende del criterio humano y de la verificación con evidencia.
6. **Trabajo futuro:** validación con origen móvil, comparar d = 0 frente a d = 1, transformaciones logarítmicas, modelos ETS o con variables exógenas.

## Referencias

- Box, G. E. P., Jenkins, G. M., Reinsel, G. C. y Ljung, G. M. (2015). *Time Series Analysis: Forecasting and Control* (5.ª ed.). Wiley.
- Hyndman, R. J. y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/
- Ljung, G. M. y Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297–303.
- Dickey, D. A. y Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- Seabold, S. y Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*. Documentación: https://www.statsmodels.org/
- Vargas, R. (2026). *No & Low Code Tools vs AI Assisted Coding* [Presentación del taller]. Maestría, Universidad Casa Grande. Archivo `No & Low Code Tools vs Al Assisted Coding.pdf`.
- Vargas, R. (2026). *sales-forecasting-demo* [Repositorio]. GitHub. https://github.com/raquelvargas16/sales-forecasting-demo
- Referencias citadas en la presentación del taller: D. Johnson, *Time-Series Analysis in Python* (Medium, 2025); I. Belcic y C. Stryker, *¿Qué es AutoML?* (IBM); *Databricks AutoML*; *How to Use AutoML to Develop ML Models*; lectura de interés: *How AI assistance impacts the formation of coding skills*.

## Anexo: reproducción

```bash
pip install -e ".[dev]"
python -m sales_forecasting --config configs/forecast.toml
pytest
```

Detalles en `docs/03-manual-instalacion-ejecucion.md`. Conversión de este informe a PDF (si se dispone de Pandoc y LaTeX): `pandoc docs/08-informe-final.md -o informe-final.pdf`.
