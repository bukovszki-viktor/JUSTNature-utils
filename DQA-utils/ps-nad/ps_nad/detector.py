import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

class PSNADetector:
    """
    Physico-Statistical NbS Anomaly Detector (PS-NAD)
    
    This class handles the statistical layer of the anomaly detection pipeline.
    It uses the Isolation Forest algorithm to identify outliers in environmental 
    sensor data without requiring labeled training sets.
    """

    def __init__(self, contamination=0.05, random_state=42):
        """
        Initialize the detector.
        
        Args:
            contamination (float): The expected proportion of outliers in the data.
            random_state (int): Seed for reproducibility.
        """
        self.model = IsolationForest(
            contamination=contamination, 
            random_state=random_state,
            n_estimators=100
        )
        self.is_trained = False

    def train(self, df, features):
        """
        Trains the Isolation Forest on 'clean' baseline data.
        
        Args:
            df (pd.DataFrame): The training dataset.
            features (list): List of column names to use for training.
        """
        if df[features].isnull().values.any():
            raise ValueError("Training data contains NaN values. Please clean the data first.")
            
        self.model.fit(df[features])
        self.is_trained = True
        print(f"Model trained successfully on {len(df)} samples using features: {features}")

    def detect(self, df, features):
        """
        Predicts anomalies in the provided dataset.
        
        Args:
            df (pd.DataFrame): The dataset to analyze.
            features (list): The features to evaluate.
            
        Returns:
            pd.Series: A series where -1 indicates an anomaly and 1 indicates normal data.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling detect().")
            
        # Returns -1 for outliers and 1 for inliers
        predictions = self.model.predict(df[features])
        return pd.Series(predictions, index=df.index)

    def get_anomaly_scores(self, df, features):
        """
        Returns the raw anomaly scores. Lower scores represent more abnormal observations.
        
        Args:
            df (pd.DataFrame): The dataset to analyze.
            features (list): The features to evaluate.
        """
        return self.model.decision_function(df[features])

    def save_model(self, folder_path, filename="baseline_v1.pkl"):
        """Saves the trained model to the models directory."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        full_path = os.path.join(folder_path, filename)
        joblib.dump(self.model, full_path)
        print(f"Model saved to {full_path}")

    @classmethod
    def load_model(cls, file_path):
        """Loads a pre-trained model from disk."""
        instance = cls()
        instance.model = joblib.load(file_path)
        instance.is_trained = True
        print(f"Model loaded from {file_path}")
        return instance

if __name__ == "__main__":
    # Example usage for testing the module independently
    print("Testing PS-NAD Detector Module...")
    
    # Generate dummy data
    data = pd.DataFrame({
        'pm25': np.random.normal(15, 2, 100),
        'temp': np.random.normal(20, 5, 100)
    })
    
    # Create an obvious outlier
    data.loc[99] = [300.0, 20.0]
    
    detector = PSNADetector(contamination=0.02)
    detector.train(data.iloc[:90], ['pm25', 'temp']) # Train on first 90 points
    
    results = detector.detect(data, ['pm25', 'temp'])
    print(f"Anomaly detected at index 99: {results.iloc[99] == -1}")