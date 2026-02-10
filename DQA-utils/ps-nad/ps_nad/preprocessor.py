import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging

class NbSPreprocessor:
    """
    Data Preprocessor for NbS Sensor Networks.
    
    Handles ingestion, timestamp normalization, outlier-safe scaling,
    and feature engineering for environmental indicators.
    """

    def __init__(self, scaling_method='standard'):
        """
        Initialize the preprocessor.
        
        Args:
            scaling_method (str): 'standard' for StandardScaler or 'minmax' for MinMaxScaler.
        """
        self.scaler = StandardScaler() if scaling_method == 'standard' else MinMaxScaler()
        self.is_fitted = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("NbSPreprocessor")

    def load_and_format(self, file_path, datetime_col='timestamp', index_is_time=True):
        """
        Loads CSV/JSON data and ensures a proper DatetimeIndex.
        
        Args:
            file_path (str): Path to the dataset.
            datetime_col (str): Column name containing time info.
            index_is_time (bool): If True, sets the datetime_col as the index.
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file format. Use .csv or .json")

            df[datetime_col] = pd.to_datetime(df[datetime_col])
            
            if index_is_time:
                df = df.set_index(datetime_col).sort_index()
                
            self.logger.info(f"Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None

    def clean_data(self, df, drop_na=False):
        """
        Basic cleaning: removes duplicates and handles missing values.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            drop_na (bool): If True, drops rows with NaNs. If False, fills with interpolation.
        """
        df = df.drop_duplicates()
        
        if drop_na:
            df = df.dropna()
        else:
            # Interpolation is better for time-series context
            df = df.interpolate(method='time').ffill().bfill()
            
        return df

    def scale_features(self, df, features, fit=True):
        """
        Applies scaling to selected features. 
        Important for Isolation Forest performance.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            features (list): Columns to scale.
            fit (bool): If True, fits the scaler to this data.
        """
        data_to_scale = df[features].copy()
        
        if fit:
            self.scaler.fit(data_to_scale)
            self.is_fitted = True
            
        scaled_data = self.scaler.transform(data_to_scale)
        
        # Return a copy with scaled values to avoid modifying original stream
        df_scaled = df.copy()
        df_scaled[features] = scaled_data
        return df_scaled

    def inverse_transform(self, scaled_values, features):
        """Converts scaled values back to original units (e.g., for reporting)."""
        if not self.is_fitted:
            raise RuntimeError("Scaler has not been fitted yet.")
        return self.scaler.inverse_transform(scaled_values)

    def add_time_features(self, df):
        """
        Extracts temporal context (hour, day of week) as numeric features.
        Useful for models to learn diurnal patterns.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            self.logger.warning("Index is not DatetimeIndex. Skipping time feature extraction.")
            return df
            
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        return df

if __name__ == "__main__":
    # Example usage
    preprocessor = NbSPreprocessor(scaling_method='minmax')
    
    # Create mock data
    mock_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2025-01-01', periods=5, freq='H'),
        'pm25': [12.5, 15.0, 100.0, 14.2, 13.8],
        'temp': [5.1, 5.5, 6.0, 5.8, 5.2]
    })
    
    # Process
    mock_data['timestamp'] = pd.to_datetime(mock_data['timestamp'])
    mock_data = mock_data.set_index('timestamp')
    
    cleaned = preprocessor.clean_data(mock_data)
    scaled = preprocessor.scale_features(cleaned, ['pm25', 'temp'])
    
    print("Original Data:\n", mock_data)
    print("\nScaled Data (ready for ML):\n", scaled)