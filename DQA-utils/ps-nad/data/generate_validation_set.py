import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_validation_set(days=7):
    """
    Generates a fresh 'Blind Test' dataset with new anomaly patterns.
    Updated to match column names in physics_rules.json.
    """
    np.random.seed(99) # Different seed for new data
    periods = days * 24
    # Starting one month after the training data
    start_date = datetime(2025, 2, 1)
    timestamps = [start_date + timedelta(hours=x) for x in range(periods)]
    
    # 1. Base Signal (Colder February weather)
    # Using PM2.5 and Temperature (match JSON keys)
    pm25 = 20 + 3 * np.sin(np.linspace(0, 2 * np.pi * days, periods)) + np.random.normal(0, 1.5, periods)
    temp = 2 + 5 * np.sin(np.linspace(0, 2 * np.pi * days, periods) - (np.pi/4)) + np.random.normal(0, 0.5, periods)
    wind_speed = np.abs(np.random.normal(3, 2, periods))

    df = pd.DataFrame({
        'timestamp': timestamps,
        'PM2.5': pm25,
        'Temperature': temp,
        'wind_speed': wind_speed
    })

    # 2. Inject 'Trap' Anomalies
    
    # Event 1: High Pollution Morning (Real Event)
    # Very cold morning, no wind, PM spikes to 95.
    df.loc[20, 'Temperature'] = -5.0
    df.loc[20, 'wind_speed'] = 0.1
    df.loc[20, 'PM2.5'] = 95.0 

    # Event 2: Battery Failure / Flatline (Hardware Error)
    # Sensor gets stuck at exactly 0.0 for 5 hours
    df.loc[80:85, 'PM2.5'] = 0.0
    
    # Event 3: Extreme Electronic Noise (Hardware Error)
    # Single hour spike to 499 (near max limit)
    df.loc[120, 'PM2.5'] = 499.0

    # 3. Save to Project Structure
    output_dir = os.path.join(os.path.dirname(__file__), 'raw')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'validation_test_set.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Validation set created at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_validation_set()