# Context-Aware Neural Imputer (CAN-Imputer)

A Generative Adversarial Imputation Net (GAIN) designed to heal gaps in environmental time-series data. It uses Physics-Informed Post-processing to ensure all imputed values obey the laws of nature.

## Documentation
*   [**Methodology**](docs/methodology.md): Explains the Generative Adversarial Network architecture, Cyclical Temporal Encoding, and Physics-Informed Gating.
*   [**Setup & Usage**](docs/setup_guide.md): Instructions for training the model, evaluating performance, and running the inference pipeline.

## Quick Start
```bash
# 1. Train Model
python train_imputer.py

# 2. Heal Data (Inference)
python inference.py
```
**Input**: Raw sensor data with gaps + PS-NAD Anomaly Report.
**Output**: A complete, physically consistent dataset.
