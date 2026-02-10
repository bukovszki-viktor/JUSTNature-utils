import numpy as np
import torch
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import ks_2samp

def calculate_rmse(target, prediction, mask):
    """
    Calculates the Root Mean Square Error only on the imputed values.
    
    Args:
        target: The ground truth data (scaled).
        prediction: The output from the Generator.
        mask: The binary mask (1 for observed, 0 for missing/imputed).
    """
    # In GAIN, we only care about the error where the data was originally missing (mask == 0)
    imputed_mask = 1 - mask
    
    # Extract only the imputed values
    target_imputed = target[imputed_mask == 1]
    prediction_imputed = prediction[imputed_mask == 1]
    
    if len(target_imputed) == 0:
        return 0.0
        
    return np.sqrt(mean_squared_error(target_imputed, prediction_imputed))

def calculate_mae(target, prediction, mask):
    """Calculates Mean Absolute Error on imputed values."""
    imputed_mask = 1 - mask
    target_imputed = target[imputed_mask == 1]
    prediction_imputed = prediction[imputed_mask == 1]
    
    if len(target_imputed) == 0:
        return 0.0
        
    return mean_absolute_error(target_imputed, prediction_imputed)

def calculate_distribution_similarity(target, prediction, mask):
    """
    Performs a Kolmogorov-Smirnov test to compare the distributions
    of real vs imputed data. 
    
    Returns:
        ks_stat: Closer to 0 means the distributions are identical.
        p_value: If > 0.05, we cannot distinguish the fake data from real data (Good).
    """
    imputed_mask = 1 - mask
    target_imputed = target[imputed_mask == 1]
    prediction_imputed = prediction[imputed_mask == 1]
    
    if len(target_imputed) < 2 or len(prediction_imputed) < 2:
        return 1.0, 0.0
        
    stat, p_val = ks_2samp(target_imputed, prediction_imputed)
    return stat, p_val

def get_imputation_performance(target_df, imputed_df, mask_df):
    """
    Returns a dictionary of comprehensive performance metrics.
    """
    results = {}
    for col in target_df.columns:
        # 1. Distance Metrics
        rmse = calculate_rmse(
            target_df[col].values, 
            imputed_df[col].values, 
            mask_df[col].values
        )
        mae = calculate_mae(
            target_df[col].values, 
            imputed_df[col].values, 
            mask_df[col].values
        )
        
        # 2. Distribution Metrics (Realism check)
        ks_stat, p_val = calculate_distribution_similarity(
            target_df[col].values, 
            imputed_df[col].values, 
            mask_df[col].values
        )
        
        results[col] = {
            "RMSE": round(rmse, 4),
            "MAE": round(mae, 4),
            "KS_Statistic": round(ks_stat, 4),
            "P_Value": round(p_val, 4),
            "Status": "Passed" if p_val > 0.05 else "Failed Realism"
        }
        
    return results