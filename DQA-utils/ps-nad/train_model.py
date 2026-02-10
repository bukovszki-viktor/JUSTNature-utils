import os
import pandas as pd
from ps_nad.preprocessor import NbSPreprocessor
from ps_nad.detector import PSNADetector

def main():
    # 1. Paths and Configuration
    data_path = "data/raw/budapest_sensor_raw.csv"
    model_dir = "models"
    # UPDATED: Feature names now match Physics Rules and Validation Sets
    features = ['PM2.5', 'Temperature', 'wind_speed']
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}. Run generate_synthetic_data.py first.")
        return

    # 2. Initialize Preprocessor and Load Data
    print("--- Step 1: Loading and Cleaning Data ---")
    preprocessor = NbSPreprocessor(scaling_method='standard')
    df = preprocessor.load_and_format(data_path)
    df = preprocessor.clean_data(df)
    
    # 3. Define the 'Clean' Training Baseline
    print(f"--- Step 2: Defining Baseline (First 400 hours) ---")
    train_df = df.iloc[:400].copy()
    
    # 4. Scale Features
    print("--- Step 3: Scaling Features ---")
    train_df_scaled = preprocessor.scale_features(train_df, features, fit=True)
    
    # 5. Initialize and Train the Detector
    print("--- Step 4: Training Isolation Forest ---")
    detector = PSNADetector(contamination=0.01)
    detector.train(train_df_scaled, features)
    
    # 6. Save the Model
    print("--- Step 5: Saving Model Assets ---")
    detector.save_model(model_dir, "baseline_v1.pkl")
    
    print(f"\nRetraining complete. Model now uses native names: {features}")

if __name__ == "__main__":
    main()