import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import logging

def arima_forecast(series, order=(1, 1, 1), steps=4):
    """
    Fit ARIMA model and forecast the next 'steps' points.
    
    :param series: pandas Series of historical data
    :param order: ARIMA order (p, d, q)
    :param steps: forecast horizon
    :return: list of forecasted values
    """
    try:
        # Ensure series is not empty and is a pandas Series with proper date index
        if series.empty:
            logging.error("The time series data is empty.")
            return [0] * steps
        
        # Fit the ARIMA model
        model = ARIMA(series, order=order)
        model_fit = model.fit()
        
        # Forecast the future values
        forecast = model_fit.forecast(steps=steps)
        
        # Return the forecasted values as a list
        return forecast.tolist()
    
    except Exception as e:
        logging.error(f"ARIMA forecasting failed: {e}")
        return [0] * steps  # Return a default list of zeros if ARIMA fails
