from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def ets_forecast(series, steps=4):
    model = ExponentialSmoothing(series, trend='add', seasonal=None)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps)

    y_true = series[-steps:]
    y_pred = model_fit.fittedvalues[-steps:]

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    print("ETS - MAE:", mae)
    print("ETS - RMSE:", rmse)

    return forecast.tolist(), mae, rmse

def ets_forecast(series, steps=4, trend='add', seasonal=None, seasonal_periods=None):
    try:
        model = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
        model_fit = model.fit()
        forecast = model_fit.forecast(steps)

        # Calculate the evaluation metrics
        y_true = series[-steps:]
        y_pred = model_fit.fittedvalues[-steps:]

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        return forecast.tolist(), mae, rmse

    except Exception as e:
        print(f"Error in ETS forecasting: {e}")
        return [None] * steps, None, None

