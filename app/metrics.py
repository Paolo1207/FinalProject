from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    
    epsilon = 1e-10
    mape = np.mean(np.abs((actual - predicted) / (actual + epsilon))) * 100
    
    try:
        r2 = r2_score(actual, predicted)
    except:
        r2 = None
    
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'MAPE (%)': mape,
        'R2': r2
    }
