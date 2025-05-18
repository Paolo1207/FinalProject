from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from app.metrics import calculate_metrics
import numpy as np

# Tuning Linear Regression by adjusting the polynomial degree
def tune_linear_regression(series, max_degree=3):
    best_score = float("inf")
    best_degree = 1
    best_model = None
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values

    for degree in range(1, max_degree+1):
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(X, y)
        y_pred = model.predict(X)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        if rmse < best_score:
            best_score = rmse
            best_degree = degree
            best_model = model
    return best_model, best_degree, best_score

# Forecasting with Linear Regression and using external metrics function for evaluation
def linear_regression_forecast(series, steps=4):
    # Use the best model or default linear regression if tuning isn't performed yet
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    model = LinearRegression()
    model.fit(X, y)

    # Predict future values
    future_X = np.arange(len(series), len(series) + steps).reshape(-1, 1)
    forecast = model.predict(future_X)

    # Predictions on existing data for evaluation
    y_pred = model.predict(X)

    # Calculate all metrics using the shared function
    metrics = calculate_metrics(y, y_pred)

    # Optionally print metrics
    print("Linear Regression Metrics:", metrics)

    # Return forecast and individual metrics (unpack as needed)
    return forecast.tolist(), metrics['MAE'], metrics['RMSE'], metrics['MAPE (%)'], metrics['R2']
