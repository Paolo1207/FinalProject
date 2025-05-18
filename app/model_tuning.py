import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import numpy as np


def tune_arima(series, p_values, d_values, q_values):
    best_score, best_cfg = float("inf"), None
    best_model = None

    warnings.filterwarnings("ignore")
    for p in p_values:
        for d in d_values:
            for q in q_values:
                try:
                    model = ARIMA(series, order=(p,d,q))
                    model_fit = model.fit()
                    predictions = model_fit.predict(start=0, end=len(series)-1)
                    rmse = np.sqrt(mean_squared_error(series, predictions))
                    if rmse < best_score:
                        best_score, best_cfg = rmse, (p,d,q)
                        best_model = model_fit
                except:
                    continue
    return best_model, best_cfg, best_score
