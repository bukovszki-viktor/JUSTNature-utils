# PS-NAD: Physico-Statistical NbS Anomaly Detector

**PS-NAD** is a hybrid anomaly detection system designed for Nature-based Solutions (NbS) sensor networks. It combines statistical machine learning (Isolation Forest) with physics-informed rules to identify and validate anomalies in environmental data streams (e.g., PM2.5, Temperature).

## Key Features

- **Hybrid Detection**:
  - **Statistical Layer**: Uses Isolation Forest to detect outliers based on distribution.
  - **Physics Layer**: Validates anomalies using physical constraints (limits, rate of change, correlations).
- ** robust Preprocessing**: Handles timestamp alignment, missing values, and scaling.
- **Explainable Output**: Classifies anomalies as "Real Events" or "Hardware Errors" with specific reasons.

## Project Structure

```
ps-nad/
├── ps_nad/                 # Main package source
│   ├── detector.py         # Isolation Forest implementation
│   ├── physics_gate.py     # Rule-based validation logic
│   ├── physics_rules.json  # Configuration for physical constraints
│   └── preprocessor.py     # Data cleaning and scaling
├── data/                   # Data directory (raw & processed)
├── models/                 # Saved model artifacts
├── tests/                  # Unit tests
├── train_model.py          # Script to train the ML detector
├── inference.py            # Script to run the full detection pipeline
└── pyproject.toml          # Package configuration
```

## Installation

This project is set up as a Python package. To install it in editable mode (recommended for development):

```bash
# From the ps-nad/ directory
pip install -e .
```

This ensures that imports like `from ps_nad import ...` work correctly across all scripts.

## Usage

### 1. Generate Synthetic Data (Optional)
If you don't have raw sensor data, you can generate a synthetic dataset for testing:
```bash
python data/generate_synthetic_data.py
python data/generate_validation_set.py
```

### 2. Train the Model
Train the Isolation Forest on a "clean" baseline dataset. This saves the model to `models/baseline_v1.pkl`.
```bash
python train_model.py
```
*Note: Ensure `data/raw/budapest_sensor_raw.csv` exists or update the path in the script.*

### 3. Run Inference
Run the full detection pipeline (Preprocessing -> ML Detection -> Physics Validation) on new data.
```bash
python inference.py
```
*Note: This reads from `data/raw/validation_test_set.csv` and outputs a report to `data/processed/anomaly_report.csv`.*

## Configuration

### Physics Rules
Physical constraints are defined in `ps_nad/physics_rules.json`. You can modify this file to adjust thresholds for different environmental variables.

**Example Rule:**
```json
"PM2.5": {
    "min_value": 0,
    "max_value": 500,
    "max_delta_per_hour": 50,
    "wind_speed_correlation": "negative"
}
```

## Testing

Run the test suite using `pytest`:
```bash
pytest
```
