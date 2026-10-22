# 04 — Metodología de pronóstico

Todas las cifras de este documento provienen de `reports/metrics.json` y `reports/arima_grid_search.csv`, generados con `python -m sales_forecasting --config configs/forecast.toml`. Las cifras marcadas con **(notebook)** provienen de las salidas del notebook ejecutado `notebooks/ventas_mensuales_live_coding.ipynb`.

## 1. Datos

| Atributo | Valor |
|---|---|
| Fuente | `src/data/stores_sales_forecasting.csv` (Superstore, categoría *Furniture*) — sin modificar |
| Registros | 2121 transacciones, 2014-01-06 a 2017-12-30 |
| Variable objetivo | `Sales` (suma mensual de ventas) |
| Fecha | `Order Date`, formato `%m/%d/%Y` |
| Lectura | latin-1, `encoding_errors="replace"` |
| Validaciones | columnas obligatorias, dataset no vacío, fechas parseables, ventas numéricas y no negativas (`data.validate_sales`) |

## 2. Granularidad y horizonte

- **Granularidad:** mensual, `freq='MS'` (inicio de mes). La serie tiene **48** observaciones, de 2014-01-01 a 2017-12-01, sin meses vacíos.
- **Horizonte:** **12 meses**, tanto en la evaluación (2017) como en el pronóstico futuro (2018).
- **Estacionalidad:** `s = 12` (anual).

El template original agregaba por semana (`freq='W'`). Se corrigió porque la consigna pide ventas mensuales y porque `s = 12` sobre datos semanales no representa un año (ver `docs/01-inventario-tecnico.md`, C-1).

## 3. Partición temporal (sin fuga de información)

| Conjunto | Meses | Periodo |
|---|---|---|
| Entrenamiento | 36 | 2014-01 a 2016-12 |
| Prueba (*hold-out*) | 12 | 2017-01 a 2017-12 (`test_start` = 2017-01-01) |

Reglas aplicadas:

1. La partición no baraja: `temporal_train_test_split` toma las últimas 12 observaciones como prueba y comprueba que `max(train) < min(test)`.
2. La prueba ADF, la búsqueda del orden por AIC, el ajuste del SARIMA y los baselines usan **solo** el entrenamiento.
3. La prueba se usa **una sola vez**, para calcular las métricas finales.
4. Para el pronóstico de 2018 se reentrena con los 48 meses manteniendo el orden ya elegido.

## 4. Análisis exploratorio y diagnóstico

### 4.1 Estacionariedad — Dickey-Fuller aumentado (ADF)

H0: la serie tiene raíz unitaria (no es estacionaria). Nivel de significación α = 0.05. Resultado del pipeline sobre el **entrenamiento**:

| Serie | Estadístico ADF | p-valor | Valor crítico 5 % | Rezagos usados | n | ¿Rechaza H0? |
|---|---|---|---|---|---|---|
| Entrenamiento en niveles | −3.8778 | 0.0022 | −2.9485 | 0 | 35 | Sí |
| Entrenamiento con diferencia estacional (y<sub>t</sub> − y<sub>t−12</sub>) | −4.4160 | 0.00028 | −2.9985 | 0 | 23 | Sí |

En el notebook, el ADF sobre la serie completa (48 meses) también rechaza H0 (p = 8.45e-05) **(notebook)**.

Lectura prudente: el ADF evalúa una raíz unitaria *regular*, no estacional; con tan pocas observaciones su potencia es baja. La estacionalidad anual es evidente en el gráfico y en la ACF, lo que justifica D = 1. La diferencia regular d = 1 del modelo de la sesión **no** la exige el ADF, por lo que existe riesgo de sobrediferenciar.

### 4.2 Descomposición

Descomposición multiplicativa con periodo 12 (`seasonal_decompose`). Índices estacionales destacados **(notebook)**: diciembre 1.998, noviembre 1.883, septiembre 1.757 (picos); febrero 0.297 y enero 0.574 (valles). Las ventas anuales pasan de 157192.85 (2014) a 215387.27 (2017) **(notebook)**: hay una tendencia creciente moderada.

### 4.3 Autocorrelación (ACF/PACF y Ljung-Box sobre la serie)

La ACF de la serie mensual vale 0.640 en el rezago 12 y 0.297 en el rezago 1 **(notebook)**: la dependencia se concentra en el rezago estacional. En la serie doblemente diferenciada (d = 1, D = 1), la ACF y la PACF solo salen con claridad de la banda en el rezago 1, lo que sugiere términos AR/MA de orden bajo. Por eso la rejilla explora p, q ∈ {0, 1, 2}.

## 5. Modelo SARIMA

Notación: SARIMA(p, d, q)×(P, D, Q, s). Se respetó la estructura de la sesión en vivo: (p, 1, q)×(0, 1, 0, 12).

**Rejilla** (`configs/forecast.toml`): p ∈ {0, 1, 2}, d ∈ {1}, q ∈ {0, 1, 2}, `seasonal_order = (0, 1, 0, 12)` → 9 combinaciones, ajustadas con `statsmodels.tsa.arima.model.ARIMA` sobre el entrenamiento y ordenadas por AIC.

| Orden (p, d, q) | AIC | BIC |
|---|---|---|
| **(0, 1, 0)** | **467.64** | 468.77 |
| (1, 1, 1) | 468.30 | 471.71 |
| (1, 1, 0) | 468.83 | 471.10 |
| (0, 1, 1) | 468.95 | 471.22 |
| (2, 1, 1) | 470.11 | 474.65 |
| (0, 1, 2) | 470.23 | 473.64 |
| (2, 1, 0) | 471.45 | 474.85 |
| (2, 1, 2) | 471.98 | 477.66 |
| (1, 1, 2) | 472.40 | 476.94 |

Fuente: `reports/arima_grid_search.csv`. Modelo elegido: **SARIMA(0, 1, 0)×(0, 1, 0, 12)**, AIC = 467.64. La diferencia con el segundo es menor que 1 punto de AIC, así que ambos son prácticamente equivalentes; el criterio favorece al más parsimonioso.

**Propiedad clave del modelo elegido.** Sin términos AR ni MA y con d = D = 1, el pronóstico es

$$\hat{y}_{T+h} = y_{T+h-12} + (y_T - y_{T-12}),$$

es decir, el *seasonal naive* más el último cambio interanual observado. En la prueba, ese cambio (diciembre 2016 − diciembre 2015) es +13592.90 **(notebook)**, y se suma a los 12 meses.

## 6. Baselines

| Baseline | Definición | Parámetro |
|---|---|---|
| *Naive* | ŷ<sub>T+h</sub> = y<sub>T</sub> | — |
| *Seasonal naive* | ŷ<sub>T+h</sub> = y<sub>T+h−12</sub> (repite el mismo mes del año anterior) | `season_length = 12` |
| Media móvil (3) | ŷ<sub>T+h</sub> = media de las 3 últimas observaciones, constante | `moving_average_window = 3` |

## 7. Métricas

Sea y<sub>t</sub> el valor real, ŷ<sub>t</sub> el pronóstico y n = 12.

$$\mathrm{MAE} = \frac{1}{n}\sum_{t=1}^{n} \lvert y_t - \hat{y}_t \rvert$$

$$\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{t=1}^{n} (y_t - \hat{y}_t)^2}$$

$$\mathrm{sMAPE} = \frac{100}{n}\sum_{t=1}^{n} \frac{2\,\lvert y_t - \hat{y}_t \rvert}{\lvert y_t \rvert + \lvert \hat{y}_t \rvert} \quad (\text{0–200 \%; los pares con denominador 0 aportan 0})$$

$$\mathrm{WAPE} = 100 \cdot \frac{\sum_{t=1}^{n} \lvert y_t - \hat{y}_t \rvert}{\sum_{t=1}^{n} \lvert y_t \rvert}$$

- MAE y RMSE están en unidades monetarias; RMSE penaliza más los errores grandes.
- sMAPE y WAPE son relativos (%); WAPE pondera por el volumen total y es más estable que el MAPE cuando hay meses con ventas bajas.
- Implementación: `src/sales_forecasting/metrics.py`. La tabla se ordena por RMSE.

## 8. Resultados (conjunto de prueba, 2017)

Fuente: `reports/metrics.json` → `metrics` (redondeo a 2 decimales).

| Modelo | MAE | RMSE | sMAPE (%) | WAPE (%) |
|---|---|---|---|---|
| **Seasonal naive** | **3747.03** | **4473.38** | **25.70** | **20.88** |
| SARIMA(0, 1, 0)×(0, 1, 0, 12) | 12219.08 | 12939.46 | 59.20 | 68.08 |
| Moving average (3) | 11688.95 | 13105.84 | 59.59 | 65.12 |
| Naive | 18792.78 | 21085.77 | 76.79 | 104.70 |

**Diagnóstico de residuos del SARIMA** (Ljung-Box sobre los residuos de entrenamiento, descartando los primeros 13 por la diferenciación):

| Rezago | Estadístico Q | p-valor |
|---|---|---|
| 6 | 13.2957 | 0.0386 |
| 12 | 26.0748 | 0.0105 |

Figuras: `reports/figures/forecast_test.png` (prueba) y `reports/figures/forecast_future.png` (2018).

## 9. Interpretación

1. **El SARIMA de la sesión en vivo no supera al *seasonal naive*.** Su RMSE (12939.46) es casi el triple del *seasonal naive* (4473.38), mejora apenas a la media móvil (13105.84) y solo supera con claridad al *naive* (21085.77). En MAE, la media móvil (11688.95) es incluso algo mejor que el SARIMA (12219.08).
2. **Causa.** Por la propiedad de la sección 5, el SARIMA copia el año anterior y le suma el salto de diciembre 2015 → diciembre 2016 (+13592.90 **(notebook)**). Ese salto no se repitió en 2017, de modo que el modelo sobreestima todo el horizonte.
3. **Residuos.** Ljung-Box rechaza H0 en los rezagos 6 (p = 0.0386) y 12 (p = 0.0105): los residuos **no** son ruido blanco y queda autocorrelación sin modelar. El modelo está incompleto.
4. **Extensión exploratoria (notebook).** Permitiendo P, Q ∈ {0, 1}, el AIC sobre el entrenamiento elige SARIMA(0, 1, 0)×(1, 1, 0, 12) (AIC 465.94), cuyos residuos ya no muestran autocorrelación significativa (Ljung-Box p = 0.1326 y 0.2575). En la prueba mejora al modelo de la sesión (RMSE 10574.03; WAPE 54.29 %), pero sigue lejos del *seasonal naive*. Es una dirección de mejora, no un modelo definitivo.
5. **Pronóstico 2018.** El SARIMA reentrenado con 48 meses suma 152132.29 para 2018 frente a 215387.27 vendidos en 2017 **(notebook)**, y sus límites inferiores del IC 95 % son negativos (`reports/forecast_future.csv`). No debería usarse para decisiones sin mejorar el modelo; la referencia más defendible con esta evidencia es el *seasonal naive*.

## 10. Limitaciones

- Serie corta: 48 meses, 36 para entrenar, solo 23 residuos útiles tras la diferenciación.
- Un único corte temporal de validación (12 meses): las métricas dependen de un solo año.
- Una sola categoría (*Furniture*) y sin variables exógenas (promociones, precios, calendario).
- Diferencias de AIC pequeñas entre los órdenes candidatos.
- Posible sobrediferenciación (d = 1 no lo exige el ADF).
- El intervalo de confianza admite valores negativos (el modelo no impone positividad).

## 11. Trabajo futuro

1. Validación cruzada temporal con origen móvil (*rolling origin*) para comparar modelos con más de un año de prueba.
2. Comparar d = 0 frente a d = 1 con D = 1.
3. Transformación logarítmica o Box-Cox para estabilizar la varianza y evitar intervalos negativos.
4. Modelos alternativos: ETS (Holt-Winters), regresión con dummies estacionales, SARIMAX con variables exógenas.
5. Repetir el análisis con las demás categorías del Superstore.
