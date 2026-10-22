"""Demo de H2O AutoML (herramienta low-code) para contrastar con el notebook ARIMA.

Uso, con el entorno virtual activo y ``pip install h2o==3.46.0.12``::

    cd h2o_demo && python main.py      # o bien: python h2o_demo/main.py desde la raíz

Requiere Java instalado (verificado con OpenJDK 21; ver reports/evidence/h2o_smoke.txt).
"""

import h2o
import os
from h2o.automl import H2OAutoML
from src.eng_sales_forecasting import preprocess_ts

class H2OAutoMLWrapper:
    """Envoltura mínima sobre H2OAutoML: importar datos, entrenar y predecir."""

    def __init__(self, data_path: str="data/"):
        """
        Inicializa la clase H2OAutoMLWrapper.

        Si ``data_path`` no es un archivo existente se usa el dataset público
        ``powerplant_output.csv`` de los tutoriales de H2O (requiere internet).
        """
        if os.path.isfile(data_path):
            self.data_path = data_path
        else:
            self.data_path = "https://github.com/h2oai/h2o-tutorials/raw/master/h2o-world-2017/automl/data/powerplant_output.csv"

    def import_data(self):
        """
        Importa los datos desde la ruta especificada y si no se proporciona
        una ruta válida, descarga los datos desde un enlace predeterminado."""
        return h2o.import_file(self.data_path)
    def run_automl(self, data,
                   target: str="HourlyEnergyOutputMW",
                   test_ratio: float=0.2,
                   seed: int=42,
                   max_runtime_secs: int=60,
                   project_name = "powerplant_lb_frame"
                   ):
        """
        Entrena H2OAutoML con una partición aleatoria train/test (``split_frame``).

        Nota: la partición aleatoria es adecuada para datos tabulares i.i.d., no para
        series de tiempo (mezcla pasado y futuro); para ventas mensuales use un corte
        temporal como en ``sales_forecasting.split.temporal_train_test_split``.
        """
        splits = data.split_frame(ratios=[1-test_ratio], seed=seed)
        train = splits[0]
        test = splits[1]
        aml = H2OAutoML(max_runtime_secs = max_runtime_secs, seed = seed, project_name = project_name)
        aml.train(y = target, training_frame = train, leaderboard_frame = test)
        return aml
    def predict(self, aml_model, new_data):
        """
        Realiza predicciones utilizando el modelo ganador del AutoML.
        """
        return aml_model.leader.predict(new_data)

if __name__ == "__main__":
    h2o.init()
    # automl_wrapper = H2OAutoMLWrapper()
    # data = automl_wrapper.import_data()
    # aml_model = automl_wrapper.run_automl(data)
    # print(aml_model.leaderboard.head(15))

    ## Prueba con serie de tiempo
    # preprocess_ts() ahora agrega por mes (freq="MS") y resuelve rutas relativas a su
    # propio archivo; antes agregaba por semana (freq="W"). Para el comportamiento
    # anterior: preprocess_ts(freq="W").
    ts_path = preprocess_ts()
    data_ts = h2o.import_file(path=ts_path)
    aml2 = H2OAutoML(max_runtime_secs = 60, seed = 42, project_name = "sales_forecasting")
    aml2.train(y = "Sales", training_frame = data_ts)
    print(aml2.leaderboard.sort(by="rmse").to_pretty_str())
    # Ojo: este rendimiento se mide sobre los mismos datos de entrenamiento (optimista);
    # no es comparable con las métricas en test del notebook ARIMA.
    print(aml2.leader.model_performance(data_ts))
