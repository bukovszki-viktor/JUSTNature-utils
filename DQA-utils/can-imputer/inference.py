import torch
import pandas as pd
import numpy as np
import os
import joblib
import sys
from src.gain import Generator
from src.postprocessor import NbSPostprocessor
from src.utils.data_loaders import prepare_imputation_data

def run_imputation(input_data_path, anomaly_report_path, model_path, preprocessor_path):
    """
    Operates the full CAN-Imputer pipeline for production:
    1. Loads raw sensor data + PS-NAD anomaly report.
    2. Injects Cyclical Temporal Context (Hour Sin/Cos).
    3. Uses saved preprocessor boundaries to prevent scale-drift.
    4. Executes GAIN Neural Imputation.
    5. Applies Physics-Informed Post-processing.
    """
    print(f"--- Starting Neural Imputation Pipeline ---")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load Preprocessor State (The 'Global Ruler')
    if not os.path.exists(preprocessor_path):
        print(f"Error: {preprocessor_path} not found. Ensure model is trained.")
        return None
    preprocessor = joblib.load(preprocessor_path)

    # 2. Load Raw Sensor Data
    df_raw = pd.read_csv(input_data_path)
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
    df_raw = df_raw.set_index('timestamp')

    # 3. Add Temporal Context (Matching Training Architecture)
    df_raw['hour_sin'] = np.sin(2 * np.pi * df_raw.index.hour / 24.0)
    df_raw['hour_cos'] = np.cos(2 * np.pi * df_raw.index.hour / 24.0)
    
    # Feature set must match the 5-column model
    features = ['PM2.5', 'Temperature', 'wind_speed', 'hour_sin', 'hour_cos']
    df_raw = df_raw[features]

    # 4. Integrate PS-NAD Anomaly Report
    anomaly_report = None
    if os.path.exists(anomaly_report_path):
        anomaly_report = pd.read_csv(anomaly_report_path)
        anomaly_report['timestamp'] = pd.to_datetime(anomaly_report['timestamp'])
        anomaly_report = anomaly_report.set_index('timestamp')
        print(f"Integrating PS-NAD Report: {len(anomaly_report)} hardware errors identified for imputation.")

    # Prepare data and the binary mask (1=observed, 0=to be imputed)
    df_with_gaps, mask = prepare_imputation_data(df_raw.copy(), anomaly_report)

    # 5. Normalization (Using production boundaries)
    df_norm = preprocessor.normalize(df_with_gaps.fillna(0), fit=False)
    x = torch.FloatTensor(df_norm.values.copy()).to(device)
    m = torch.FloatTensor(mask.values.copy()).to(device)

    # 6. Load Trained GAIN Generator
    generator = Generator(len(features)).to(device)
    if not os.path.exists(model_path):
        print(f"Error: Model weights not found at {model_path}.")
        return None

    generator.load_state_dict(torch.load(model_path, map_location=device))
    generator.eval()

    # 7. Neural Imputation (Inference)
    with torch.no_grad():
        # Inject standard 0.01 jitter for validated realism
        z = torch.randn(x.shape).to(device) * 0.01
        imputed_norm = generator(x * m + z * (1 - m), m)
        final_norm = x * m + imputed_norm * (1 - m)
    
    # 8. Denormalize and Post-process
    df_imputed = preprocessor.denormalize(pd.DataFrame(final_norm.cpu().numpy(), 
                                                       index=df_raw.index, 
                                                       columns=df_raw.columns))

    print("Refining via Physics-Informed Postprocessing...")
    postprocessor = NbSPostprocessor()
    df_final = postprocessor.process_imputed_stream(df_imputed, mask)

    print("\nSUCCESS: Pipeline complete. All gaps identified by PS-NAD have been neural-filled.")
    return df_final

if __name__ == "__main__":
    # Pipeline Paths
    INPUT_FILE = "../ps-nad/data/raw/validation_test_set.csv"
    ANOMALY_REPORT = "../ps-nad/data/processed/anomaly_report.csv"
    MODEL_WEIGHTS = "models/generator_v1.pth"
    PREPROCESSOR = "models/preprocessor.pkl"
    OUTPUT_FILE = "data/processed/imputed_nbs_data.csv"

    os.makedirs("data/processed", exist_ok=True)

    final_data = run_imputation(INPUT_FILE, ANOMALY_REPORT, MODEL_WEIGHTS, PREPROCESSOR)
    
    if final_data is not None:
        # Save only the columns relevant for the rest of the toolkit
        final_data[['PM2.5', 'Temperature', 'wind_speed']].to_csv(OUTPUT_FILE)
        print(f"Saved production dataset to: {OUTPUT_FILE}")