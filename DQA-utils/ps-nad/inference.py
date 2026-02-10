import pandas as pd
import os
import sys
from ps_nad.preprocessor import NbSPreprocessor
from ps_nad.detector import PSNADetector
from ps_nad.physics_gate import PhysicsGate

def run_inference(input_data_path, model_path, rules_path):
    """
    Operates the full PS-NAD pipeline:
    Preprocessing -> ML Detection -> Physics-Informed Validation.
    Note: Model must be trained with capitalized names (PM2.5, Temperature).
    """
    print(f"--- Starting Inference on: {os.path.basename(input_data_path)} ---")
    
    # 1. Initialize Components
    preprocessor = NbSPreprocessor(scaling_method='standard')
    physics_gate = PhysicsGate(rules_path=rules_path)
    
    # Load the pre-trained ML model
    if not os.path.exists(model_path):
        print(f"Error: Trained model not found at {model_path}. Please run train_model.py first.")
        sys.exit(1)
        
    detector = PSNADetector.load_model(model_path)

    # 2. Load and Preprocess Incoming Data
    df_raw = preprocessor.load_and_format(input_data_path)
    if df_raw is None:
        return None
        
    df_clean = preprocessor.clean_data(df_raw)
    
    # Features aligned with physics_rules.json and retraining baseline
    features = ['PM2.5', 'Temperature', 'wind_speed']
    
    # Check if required features are present
    missing_cols = [f for f in features if f not in df_clean.columns]
    if missing_cols:
        print(f"Error: Missing columns {missing_cols} in {input_data_path}")
        return None

    # 3. Scaling
    # We now scale features directly using the capitalized names
    df_scaled = preprocessor.scale_features(df_clean, features, fit=True)

    # 4. Statistical Detection (ML Layer)
    print("Step 1: Running Statistical Anomaly Detection (Isolation Forest)...")
    df_clean['ml_prediction'] = detector.detect(df_scaled, features)
    df_clean['anomaly_score'] = detector.get_anomaly_scores(df_scaled, features)

    # Identify indices flagged as statistical anomalies (-1)
    ml_anomalies = df_clean[df_clean['ml_prediction'] == -1].index
    print(f"Found {len(ml_anomalies)} statistical anomalies.")

    # 5. Physical Validation (Physics Layer)
    print("Step 2: Filtering via Physics-Informed Gating (PIG)...")
    validation_report = physics_gate.process_anomalies(
        df=df_clean, 
        anomaly_indices=ml_anomalies, 
        target_col='PM2.5', 
        proxy_cols=['wind_speed']
    )

    # 6. Output and Summary
    if not validation_report.empty:
        print("\n--- DETAILED ANOMALY REPORT ---")
        print(validation_report[['value', 'status', 'reason']])
        
        real_events = len(validation_report[validation_report['status'] == "Real Event"])
        hw_errors = len(validation_report[validation_report['status'] == "Hardware Error"])
        print(f"\nConclusion: {real_events} Real Environmental Events | {hw_errors} Hardware/Sensor Errors")
    else:
        print("\nNo anomalies detected. The data stream is physically and statistically consistent.")

    return validation_report

if __name__ == "__main__":
    # Define system paths
    INPUT_FILE = "data/raw/validation_test_set.csv"
    MODEL_FILE = "models/baseline_v1.pkl"
    RULES_FILE = "ps_nad/physics_rules.json"
    OUTPUT_REPORT = "data/processed/anomaly_report.csv"
    
    # Ensure processed directory exists
    os.makedirs("data/processed", exist_ok=True)
    
    # Run the inference engine
    report = run_inference(INPUT_FILE, MODEL_FILE, RULES_FILE)
    
    # Save the results
    if report is not None and not report.empty:
        report.to_csv(OUTPUT_REPORT)
        print(f"\nFull validation report saved to: {OUTPUT_REPORT}")