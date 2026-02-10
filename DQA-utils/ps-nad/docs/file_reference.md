# PS-NAD Code Reference

This document describes the responsibility of every Python file in the **Physico-Statistical NbS Anomaly Detector (PS-NAD)** library.

## 1. Root Directory (`ps-nad/`)

### `inference.py`
**Responsibility**: The main entry point for running the anomaly detection pipeline on new data.
*   **Key Functions**: `run_inference()`
*   **Process**: Loads data -> Preprocesses -> Detects Anomalies (ML) -> Validates with Physics -> Outputs Report.

### `train_model.py`
**Responsibility**: Script to train the Isolation Forest model on baseline data.
*   **Key Functions**: `train_pipeline()`
*   **Process**: Loads baseline data -> Trains `PSNADetector` -> Saves model artifact to `models/`.

### `pytest.ini`
**Responsibility**: Configuration file for the `pytest` runner.
*   **Key Settings**: Sets `pythonpath = .` to ensure `src` modules can be imported during testing.

## 2. Source Code (`ps-nad/src/`)

### `detector.py`
**Responsibility**: Encapsulates the Machine Learning logic (Isolation Forest).
*   **Key Class**: `PSNADetector`
*   **Methods**: `train()`, `detect()`, `save_model()`, `load_model()`.

### `physics_gate.py`
**Responsibility**: Implements the Physics-Informed Gating (PIG) layer.
*   **Key Class**: `PhysicsGate`
*   **Methods**: `validate_event()`, `process_anomalies()`.
*   **Logic**: Checks stability (Rate of Change), hard limits, and consistency against a rules file (`physics_rules.json`).

### `preprocessor.py`
**Responsibility**: Handles data cleaning, formatting, and feature engineering.
*   **Key Class**: `NbSPreprocessor`
*   **Methods**: `load_and_format()`, `clean_data()`, `scale_features()`.

### `__init__.py`
**Responsibility**: Marks the directory as a Python package, allowing imports like `from src.detector import ...`.

## 3. Tests (`ps-nad/tests/`)

### `test_detector.py`
**Responsibility**: Unit tests for the `PSNADetector` class.
*   **Coverage**: Verifies model training, prediction shape, and error handling for untrained models.

### `test_physics.py`
**Responsibility**: Unit tests for the `PhysicsGate` class.
*   **Coverage**: Verifies that physical rules (Hard Limits, Rate of Change) correctly flag impossible values.

## 4. Configuration Files

### `src/physics_rules.json`
**Responsibility**: The "Laws of Nature" configuration file used by `PhysicsGate`.
*   **Content**: Defines valid ranges (`min_value`, `max_value`) and dynamic constraints (`max_delta_per_hour`) for variables like PM2.5, Temperature, and Soil Moisture.
*   **Usage**: Loaded at runtime to validate sensor readings.

### `requirements.txt`
**Responsibility**: Lists the external Python dependencies required to run the project.
*   **Key Libraries**: `pandas`, `numpy`, `scikit-learn`, `joblib`.

## 5. Setup & Utility Scripts

### `create_ps_nad.ps1`
**Responsibility**: PowerShell script to scaffold the `ps-nad` directory structure.
*   **Usage**: Executed once to generate the initial folders and placeholder files.

### `create_imputer.ps1`
**Responsibility**: PowerShell script to scaffold the sibling `can-imputer` project.
*   **Usage**: Generates the folder structure and core GAIN model files (`gain.py`, `preprocessor.py`) for the imputation tool.
