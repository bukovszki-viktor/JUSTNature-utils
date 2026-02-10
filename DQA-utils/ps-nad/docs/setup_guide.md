# Setup Guide: PS-NAD

## Prerequisites
- **Python 3.8+**
- **pip** (Python package manager)
- **Virtual Environment** (recommended)

## 1. Installation

### Clone and Navigate
```bash
git clone <repository-url>
cd ps-nad/ps-nad
```

### Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 2. Usage

### A. Data Generation
Since this is a standalone demo, start by generating synthetic data:
```bash
# Generate training data (Baseline)
python data/generate_synthetic_data.py
# Output: data/raw/budapest_sensor_raw.csv

# Generate validation data (Blind Test Set)
python data/generate_validation_set.py
# Output: data/raw/validation_test_set.csv
```

### B. Training the Model
Train the Isolation Forest on the baseline data:
```bash
python train_model.py
```
*   **Artifacts**: Creates `models/baseline_v1.pkl`

### C. Running Inference
Run the full pipeline (Preprocessing -> ML -> Physics Gate) on the validation set:
```bash
python inference.py
```
*   **Output**: Console report + `data/processed/anomaly_report.csv`

---

## 3. Testing
Run the unit test suite to verify system integrity:
```bash
pytest
```
Expected output: All tests passed (green).
