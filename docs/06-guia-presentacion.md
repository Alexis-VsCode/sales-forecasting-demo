# 06 — Guía de presentación (7–10 minutos)

Guion para exponer y defender el trabajo **S1-Notebook: Modelo ARIMA para predicción de ventas mensuales** ante la docente. Las cifras provienen de `reports/metrics.json` y de las salidas del notebook.

## 1. Preparación (antes de la clase)

```bash
# Linux/macOS: source .venv/bin/activate     Windows: .\.venv\Scripts\Activate.ps1
python -m sales_forecasting --config configs/forecast.toml --output-dir /tmp/demo   # Windows: --output-dir demo
pytest -m "not integration"
```

- Dejar abiertos en VS Code: `notebooks/ventas_mensuales_live_coding.ipynb` (ya ejecutado), `src/sales_forecasting/arima.py`, `configs/forecast.toml`, `reports/figures/forecast_test.png` y `docs/04-metodologia-pronostico.md`.
- Tener a mano `entrega/S1_Notebook_ARIMA_ventas_mensuales.pdf` por si falla el entorno.
- Ensayar con cronómetro.

## 2. Guion

| Min. | Bloque | Qué mostrar | Qué decir (idea central) |
|---|---|---|---|
| 0:00–0:45 | Contexto | README (sección *Objetivo*) | "La tarea pide usar GitHub Copilot Chat para construir un ARIMA que pronostique ventas **mensuales**. Partí del template del taller y lo llevé a un proyecto reproducible." |
| 0:45–2:00 | Hallazgo del template | Celda de agregación del notebook (`freq='MS'`) y `docs/01-inventario-tecnico.md` (C-1, C-2) | "El template agregaba por **semana** y la ruta `../../src/data/` no existía. Con datos semanales, s = 12 no es un año. Lo corregí: 48 meses, de 2014-01 a 2017-12." |
| 2:00–3:30 | Exploración | Gráfico de la serie, descomposición, ACF | "Hay una estacionalidad anual fuerte (diciembre 1.998, febrero 0.297; ACF 0.640 en el rezago 12). El ADF rechaza la raíz unitaria, pero lo leo con cautela: tiene poca potencia con 48 datos." |
| 3:30–5:00 | Modelo | Celda de la rejilla y `arima.py` | "Partición temporal 36/12, sin barajar. Elegí el orden por AIC **solo con el entrenamiento**: SARIMA(0,1,0)×(0,1,0,12), AIC 467.64." |
| 5:00–6:30 | Resultados | Tabla de métricas y `forecast_test.png` | "El **seasonal naive** gana: RMSE 4473.38 frente a 12939.46 del SARIMA. El SARIMA copia el año anterior y le suma un salto atípico de 2016. Ljung-Box (p = 0.0386 y 0.0105) confirma autocorrelación remanente." |
| 6:30–7:30 | Ingeniería | Terminal: `python -m sales_forecasting ...` y `pytest` | "El código del notebook está en un paquete con pruebas, configuración TOML y CI. Cualquiera puede regenerar las cifras." |
| 7:30–9:00 | Reflexión del taller | Sección 4 de esta guía | Copilot frente a H2O AutoML: qué aceleró la IA y dónde hizo falta criterio humano. |
| 9:00–10:00 | Cierre | Conclusiones del notebook | "Un modelo más complejo no siempre gana. Reportar con honestidad que el SARIMA no supera al baseline es parte del resultado." |

## 3. Mensajes clave

1. **Mensual, no semanal**: se corrigió el defecto del template que contradecía la consigna.
2. **Sin fuga temporal**: el orden se eligió solo con 2014–2016; 2017 se usó una vez.
3. **Siempre comparar contra baselines**: el *seasonal naive* (RMSE 4473.38) supera al SARIMA (RMSE 12939.46).
4. **Diagnóstico honesto**: residuos con autocorrelación; el modelo de la sesión está incompleto.
5. **La IA acelera, el criterio humano valida**: cada cifra se verificó ejecutando el código.

## 4. Reflexión: Low/No-Code (H2O AutoML) vs AI-Assisted Coding (Copilot)

Basado en la presentación del taller (`No & Low Code Tools vs Al Assisted Coding.pdf`).

| Aspecto | Low/No-Code — H2O AutoML | AI-Assisted — GitHub Copilot Chat |
|---|---|---|
| A quién va dirigido (PDF, Tema 4) | Analistas y *business users* con poco o nulo conocimiento de programación | Desarrolladores, *data scientists*, ML engineers |
| Pros citados en el PDF | MVP rápido; no requiere programar; modelos listos para producción; menos *debugging*; bueno para un baseline | Contexto del proyecto; velocidad; flexibilidad; educación (explica el código); versatilidad de lenguajes |
| Contras citados en el PDF | Poca personalización; caja negra; ingeniería de características restringida; costo; *vendor lock-in* | Alucinaciones (imports inexistentes, lógica incorrecta); riesgo de exponer secretos; "miopía de arquitectura"; costo de tokens; se queda corto en problemas complejos |
| Lo observado en este proyecto | `h2o_demo/main.py` usa `split_frame` aleatorio (mezcla pasado y futuro) y evalúa sobre los datos de entrenamiento: un AutoML genérico no impone la disciplina temporal que exige un pronóstico. Requiere Java (verificado con OpenJDK 21). | El asistente aceleró el código repetitivo (métricas, gráficos, pruebas), pero el template ya traía decisiones erróneas (`'W'`, ruta rota) que un asistente puede reproducir si no se le da el contexto. La elección sin fuga, los baselines y la lectura de residuos fueron decisiones humanas. |

Conclusión de la reflexión: el PDF ubica a la IA asistida en tests, documentación, *refactoring*, *boilerplate* y búsqueda de bugs, y reserva para la programación tradicional las decisiones de arquitectura, la lógica de negocio compleja y el conocimiento específico del negocio. Este proyecto lo confirma: Copilot fue útil para escribir; la validez metodológica dependió del criterio humano.

## 5. Preguntas probables y respuestas

1. **¿Por qué agregó por mes si el template usaba semanas?**
   La consigna pide ventas mensuales y el modelo usa s = 12. Con semanas, s = 12 sería un ciclo de 12 semanas, sin sentido de negocio. Con `freq='MS'` se obtienen 48 meses sin huecos.

2. **¿Cómo evitó la fuga de información?**
   Partición temporal (36 meses de entrenamiento, 12 de prueba), sin barajar. La rejilla AIC, el ADF y los baselines usan solo el entrenamiento. Una prueba automatizada verifica que el entrenamiento termina antes de la prueba.

3. **¿Por qué SARIMA(0,1,0)×(0,1,0,12)?**
   Fue el de menor AIC (467.64) en la rejilla p, q ∈ {0, 1, 2} con d = 1 y la parte estacional de la sesión. El segundo, (1,1,1), tiene AIC 468.30: prácticamente empatados, y se prefiere el más simple.

4. **Si el SARIMA pierde contra el *seasonal naive*, ¿el trabajo fracasó?**
   No. El objetivo es construir y evaluar el modelo con rigor. Detectar que no supera a una referencia simple es un resultado válido y evita usar un modelo peor en la práctica. Además, se explica la causa (sección 9 de `docs/04-metodologia-pronostico.md`).

5. **¿Por qué el SARIMA es peor?**
   Sin términos AR/MA y con d = D = 1, pronostica "el mismo mes del año anterior más el último cambio interanual". Ese cambio (+13592.90 entre diciembre de 2015 y diciembre de 2016) fue atípico y se arrastró a todo 2017.

6. **¿Qué dice el test de Ljung-Box de los residuos?**
   p = 0.0386 (rezago 6) y p = 0.0105 (rezago 12), ambos < 0.05: se rechaza que sean ruido blanco. Queda estructura sin modelar.

7. **El ADF dice que la serie es estacionaria. ¿Por qué diferenciar?**
   El ADF evalúa raíz unitaria regular y tiene poca potencia con pocos datos; la estacionalidad anual es clara en la ACF (0.640 en el rezago 12), por eso D = 1. Reconozco el riesgo de sobrediferenciar con d = 1; está en el trabajo futuro.

8. **¿Por qué usar sMAPE y WAPE además de MAE y RMSE?**
   MAE y RMSE están en dólares y dependen de la escala; sMAPE y WAPE son relativos y permiten comparar. WAPE pondera por volumen y es más estable que el MAPE en meses de ventas bajas.

9. **¿Cómo mejoraría el modelo?**
   Validación *rolling origin*, probar d = 0, transformación logarítmica, términos estacionales P/Q (en el notebook, SARIMA(0,1,0)×(1,1,0,12) baja el RMSE a 10574.03, aún lejos del baseline), ETS o variables exógenas.

10. **¿Qué parte hizo Copilot y qué parte hizo usted?**
    Copilot Chat se usó en la sesión en vivo para generar código (pruebas estadísticas, rejilla, gráficos). La versión final se revisó con un asistente de código de IA. Las decisiones de frecuencia, partición, baselines e interpretación se verificaron contra las salidas reales; ninguna cifra se copió de la IA sin ejecutar el código.

11. **¿Por qué no usó H2O AutoML para el pronóstico?**
    La consigna S1 pide ARIMA. Además, la demo de H2O usa partición aleatoria y evalúa sobre el entrenamiento, lo que no es válido para series de tiempo. H2O queda como componente opcional; verifiqué que arranca con Java 21.

12. **El README original pedía Java 27. ¿Por qué usa Java 21?**
    Porque lo verifiqué: H2O 3.46.0.12 arrancó y se apagó correctamente con OpenJDK 21 (`reports/evidence/h2o_smoke.txt`). Y el núcleo ARIMA no necesita Java.

13. **¿Cómo se reproduce todo?**
    `pip install -e ".[dev]"`, `python -m sales_forecasting --config configs/forecast.toml` y `pytest`. Una prueba de integración comprueba que el código actual regenera las cifras de `reports/metrics.json`.

14. **¿Hay datos personales?**
    El CSV del Superstore incluye nombres de clientes de muestra (conjunto público de demostración). El modelo solo usa fecha y ventas, y no se publican datos nuevos.

## 6. Plan B si falla la demo en vivo

- Mostrar `entrega/S1_Notebook_ARIMA_ventas_mensuales.pdf`.
- Mostrar `reports/metrics.csv` y las figuras de `reports/figures/`.
- Explicar el comando que habría ejecutado y la prueba que verifica la reproducibilidad.
