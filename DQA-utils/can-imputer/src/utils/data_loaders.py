import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

class NbSDataset(Dataset):
    """
    Custom Dataset for NbS Sensor Data.
    Handles data and masks for GAIN training.
    """
    def __init__(self, data, mask):
        self.data = torch.FloatTensor(data.values)
        self.mask = torch.FloatTensor(mask.values)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.mask[idx]

def prepare_imputation_data(sensor_df, anomaly_report=None):
    """
    Prepares the data and mask matrices.
    
    Args:
        sensor_df: The raw sensor dataframe.
        anomaly_report: Optional PS-NAD report to set specific bits to 0 (missing).
    """
    # Create initial mask (1 for valid, 0 for NaN)
    mask = 1 - sensor_df.isna().astype(float)
    
    # If we have an anomaly report, mask those hardware errors as missing
    if anomaly_report is not None:
        for timestamp in anomaly_report.index:
            if timestamp in mask.index:
                # We assume we are imputing the 'PM2.5' column specifically
                mask.loc[timestamp, 'PM2.5'] = 0.0
                sensor_df.loc[timestamp, 'PM2.5'] = np.nan

    return sensor_df, mask