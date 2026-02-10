import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_nbs_dataset(days=30, city="Budapest"):
    """
    Generates a synthetic dataset for NbS monitoring with injected anomalies.
    Updated to use capitalized feature names: PM2.5, Temperature, wind_speed.
    """
    np.random.seed(42)
    periods = days * 24
    timestamps = [datetime(2025, 1, 1) + timedelta(hours=x) for x in range(periods)]
    
    # 1. Base Signal Generation (Diurnal Cycles)
    hour_effect_pm = 5 * np.sin(np.linspace(0, 2 * np.pi * days, periods) + (np.pi / 2))
    pm25 = 15 + hour_effect_pm + np.random.normal(0, 2, periods)
    
    hour_effect_temp = 10 * np.sin(np.linspace(0, 2 * np.pi * days, periods) - (np.pi / 4))
    temp = 10 + hour_effect_temp + np.random.normal(0, 1, periods)
    
    wind_speed = np.abs(np.random.normal(5, 3, periods))

    # Match keys in physics_rules.json
    df = pd.DataFrame({
        'timestamp': timestamps,
        'PM2.5': pm25,
        'Temperature': temp,
        'wind_speed': wind_speed
    })

    # 2. Inject Anomalies
    df.loc[100, 'PM2.5'] = 85.0
    df.loc[100, 'wind_speed'] = 0.5 
    df.loc[250, 'PM2.5'] = 300.0
    df.loc[400, 'PM2.5'] = -10.0
    
    drift = np.linspace(0, 25, periods - 500)
    df.loc[500:, 'PM2.5'] += drift

    df.loc[df['PM2.5'] < 0, 'PM2.5'] = 0
    df.loc[400, 'PM2.5'] = -10.0 # Re-apply error

    output_dir = os.path.join(os.path.dirname(__file__), 'raw')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'budapest_sensor_raw.csv')
    df.to_csv(output_path, index=False)
    print(f"Training dataset generated with new names: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_nbs_dataset()