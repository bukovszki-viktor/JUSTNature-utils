import torch
import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
from src.gain import Generator
from src.postprocessor import NbSPostprocessor
from src.utils.metrics import get_imputation_performance

def get_quality_grade(rmse, p_value):
    """Assigns a JUSTNature Quality Grade based on scientific benchmarks."""
    if p_value < 0.05:
        return "⚠️ FAILED REALISM"
    
    if rmse < 5:
        return "🌟 GOLD STANDARD (Excellent)"
    elif rmse < 10:
        return "✅ SILVER GRADE (Good)"
    else:
        return "🥉 BRONZE GRADE (Acceptable)"

def run_evaluation(data_path, model_path, preprocessor_path):
    """
    Final Validated Evaluation:
    Assesses the model against JUSTNature Task 3.4 Scientific Standards.
    """
    print(f"--- Running Final JUSTNature Validation Pipeline ---")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not os.path.exists(preprocessor_path):
        print("Error: Fitted preprocessor.pkl not found.")
        return
    preprocessor = joblib.load(preprocessor_path)

    # 1. Data Prep & Context Encoding
    df_true = pd.read_csv(data_path)
    df_true['timestamp'] = pd.to_datetime(df_true['timestamp'])
    df_true = df_true.set_index('timestamp')
    
    # Cyclical Time Encoding
    df_true['hour_sin'] = np.sin(2 * np.pi * df_true.index.hour / 24.0)
    df_true['hour_cos'] = np.cos(2 * np.pi * df_true.index.hour / 24.0)
    
    features = ['PM2.5', 'Temperature', 'wind_speed', 'hour_sin', 'hour_cos']
    df_true = df_true[features]

    # 2. Define Validation Gap
    start_idx, gap_size = 200, 24
    df_with_gap = df_true.copy()
    mask = pd.DataFrame(1, index=df_true.index, columns=df_true.columns)
    mask.iloc[start_idx:start_idx+gap_size, 0] = 0
    df_with_gap.iloc[start_idx:start_idx+gap_size, 0] = np.nan

    # 3. Model Inference
    df_norm = preprocessor.normalize(df_with_gap.fillna(0), fit=False)
    x = torch.FloatTensor(df_norm.values.copy()).to(device)
    m = torch.FloatTensor(mask.values.copy()).to(device)

    generator = Generator(len(features)).to(device)
    generator.load_state_dict(torch.load(model_path, map_location=device))
    generator.eval()

    with torch.no_grad():
        # Using the validated 0.01 jitter for realistic texture
        z = torch.randn(x.shape).to(device) * 0.01
        imputed_norm = generator(x * m + z * (1 - m), m)
        final_norm = x * m + imputed_norm * (1 - m)
    
    df_final = preprocessor.denormalize(pd.DataFrame(final_norm.cpu().numpy(), 
                                                     index=df_true.index, 
                                                     columns=df_true.columns))
    
    # 4. Post-processing & Metric Calculation
    post = NbSPostprocessor()
    df_final = post.process_imputed_stream(df_final, mask)
    performance = get_imputation_performance(df_true, df_final, mask)
    p = performance['PM2.5']
    grade = get_quality_grade(p['RMSE'], p['P_Value'])
    
    # 5. Final Report Printing
    print("\n" + "█"*45)
    print("      JUSTNature SCIENTIFIC VALIDATION REPORT")
    print("█"*45)
    print(f"  Target Indicator:  PM2.5")
    print(f"  Accuracy (RMSE):   {p['RMSE']:.4f} μg/m³")
    print(f"  Realism (K-S):     {p['KS_Statistic']:.4f}")
    print(f"  Scientific Prob:   {p['P_Value']:.4f}")
    print(f"  Final Status:      {p['Status']}")
    print(f"  Quality Grade:     {grade}")
    print("█"*45 + "\n")

    # 6. High-Contrast Brand Plotting
    plt.figure(figsize=(12, 5), facecolor='white')
    view = slice(start_idx-24, start_idx+48)
    
    plt.plot(df_true.index[view], df_true['PM2.5'].iloc[view], 
             color='black', alpha=0.3, linestyle='--', label='Ground Truth (Sensor)')
    
    plt.plot(df_final.index[start_idx:start_idx+gap_size], 
             df_final['PM2.5'].iloc[start_idx:start_idx+gap_size], 
             color='#4831D4', linewidth=3, label='CAN-Imputer (GAIN)')
    
    plt.axvspan(df_true.index[start_idx], df_true.index[start_idx+gap_size], 
                color='#4831D4', alpha=0.05, label='Validated Imputation Gap')
    
    local_max = df_true['PM2.5'].iloc[view].replace(300, 0).max() + 10
    plt.ylim(0, local_max)
    plt.grid(True, alpha=0.15)
    plt.legend(frameon=True, facecolor='white', edgecolor='#4831D4')
    plt.title("JUSTNature CAN-Imputer: Validated Environmental Performance", fontweight='bold')
    plt.ylabel("Concentration ($\mu g/m^3$)")
    
    os.makedirs("docs", exist_ok=True)
    plt.savefig("docs/imputation_eval_plot.png", dpi=300)
    print(f"Final validation plot generated: docs/imputation_eval_plot.png")

if __name__ == "__main__":
    run_evaluation(
        "../ps-nad/data/raw/budapest_sensor_raw.csv", 
        "models/generator_v1.pth", 
        "models/preprocessor.pkl"
    )