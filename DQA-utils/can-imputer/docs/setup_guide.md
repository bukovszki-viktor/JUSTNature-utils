# CAN-Imputer Setup & User Guide

## 1. Installation
The CAN-Imputer shares the same environment as the rest of the ML Toolbox.

```bash
# Ensure you are in the project root
cd ml_toolbox
source .venv/Scripts/activate
pip install -r requirements.txt
```

## 2. Training the Model
To train the GAIN neural network on your specific dataset:

```bash
cd can-imputer
python train_imputer.py
```
*   **Input**: `../ps-nad/data/raw/validation_test_set.csv` (Uses this as the ground truth).
*   **Process**: 
    1.  Introduce artificial gaps (masking) into the data.
    2.  Train the Generator to fill gaps and Discriminator to spot fakes.
    3.  Report RMSLE loss after every 100 epochs.
*   **Artifacts**: Saves model weights to `models/generator_v1.pth` and scaled preprocessor to `models/preprocessor.pkl`.

## 3. Evaluation
Validate the model's accuracy against scientific benchmarks.

```bash
python evaluate_imputer.py
```
*   **Metrics**: Calculates RMSE, MAE, and plotting Distribution fidelity.
*   **Result**: Generates scatter plots and time-series comparisons in `docs/evaluation_plots`.

## 4. Production Inference
To heal a real data stream (filling gaps identified by PS-NAD):

```bash
python inference.py
```
*   **Inputs**: 
    *   Raw Data: `../ps-nad/data/raw/validation_test_set.csv`
    *   Anomaly Report: `../ps-nad/data/processed/anomaly_report.csv`
*   **Output**: `data/processed/imputed_nbs_data.csv` (Complete, physically valid dataset).

## 5. Master Pipeline Integration
For end-to-end operation (Detection + Imputation), use the toolbox master script:

```bash
cd ..
python master_pipeline.py
```
This automatically routes PS-NAD anomalies into the CAN-Imputer for healing.
