import os
import torch
import pandas as pd
import numpy as np
from src.trainer import GAINTrainer
from src.preprocessor import NbSPreprocessor

def train_imputer(data_path, iterations=15000, batch_size=64, miss_rate=0.2, alpha=100):
    """
    STABLE CALIBRATION TRAINING:
    - Alpha back to 100 to fix 'Extreme' drift.
    - Slower D learning rate to fix 'Zero Loss' trap.
    """
    print(f"--- Starting Stable Calibration Training for CAN-Imputer ---")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load Data
    df_raw = pd.read_csv(data_path)
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
    df_raw = df_raw.set_index('timestamp')
    df_raw['hour_sin'] = np.sin(2 * np.pi * df_raw.index.hour / 24.0)
    df_raw['hour_cos'] = np.cos(2 * np.pi * df_raw.index.hour / 24.0)
    features = ['PM2.5', 'Temperature', 'wind_speed', 'hour_sin', 'hour_cos']
    df_raw = df_raw[features]

    # 2. Preprocess
    preprocessor = NbSPreprocessor()
    df_norm = preprocessor.normalize(df_raw, fit=True)
    
    # 3. Trainer
    trainer = GAINTrainer(input_dim=len(features), alpha=alpha, lr=0.001)
    data_values = torch.FloatTensor(df_norm.values.copy()).to(device)
    
    for i in range(iterations):
        idx = np.random.choice(len(data_values), batch_size)
        x_batch = data_values[idx]
        
        # Random Masking (focused on PM2.5)
        m_batch = (torch.rand(batch_size, len(features)) > miss_rate).float().to(device)
        m_batch[:, 1:] = 1.0 
        
        # Only update D every 5 steps to handicap it further
        train_d = (i % 5 == 0)
        d_loss, g_loss = trainer.train_step(x_batch, m_batch, train_d=train_d)
        
        if i % 2000 == 0:
            print(f"Iter {i:5d} | D_Loss: {d_loss:.4f} | G_Loss: {g_loss:.4f}")

    # 4. Save
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    trainer.save_models(os.path.join(model_dir, "generator_v1.pth"), 
                        os.path.join(model_dir, "discriminator_v1.pth"))
    
    import joblib
    joblib.dump(preprocessor, os.path.join(model_dir, "preprocessor.pkl"))
    print("Training complete with Stable Calibration.")

if __name__ == "__main__":
    train_imputer(data_path="../ps-nad/data/raw/budapest_sensor_raw.csv")