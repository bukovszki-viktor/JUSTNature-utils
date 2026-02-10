import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

class NbSPreprocessor:
    """
    Standardized Preprocessor for JUSTNature Toolkit.
    Now supports persistence of scaling boundaries to prevent 'Scale Drift' 
    between training and evaluation.
    """

    def __init__(self):
        self.scaler = MinMaxScaler()
        self.is_fitted = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("NbSPreprocessor")

    def load_and_format(self, file_path):
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()
        return df

    def normalize(self, df, fit=True):
        """
        Scales data to [0, 1].
        If fit=False, it uses the boundaries from a previous training run.
        """
        if fit:
            self.scaler.fit(df)
            self.is_fitted = True
        elif not self.is_fitted:
            self.logger.warning("Attempting to normalize with unfitted scaler. Fitting now...")
            self.scaler.fit(df)
            
        return pd.DataFrame(self.scaler.transform(df), index=df.index, columns=df.columns)

    def denormalize(self, df_norm):
        """Converts [0, 1] back to physical units (ug/m3, Celsius, etc)."""
        return pd.DataFrame(self.scaler.inverse_transform(df_norm), 
                            index=df_norm.index, columns=df_norm.columns)