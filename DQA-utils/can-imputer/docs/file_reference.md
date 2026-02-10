# CAN-Imputer Code Reference

This document describes the responsibility of every file in the **Context-Aware Neural Imputer (CAN-Imputer)** library.

## 1. Root Directory (`can-imputer/`)

### `train_imputer.py`
**Responsibility**: Script to train the GAIN model on a specific dataset.
*   **Key Functions**: `main()`
*   **Process**: Loads data -> Introduces artificial gaps (masking) -> Trains Generator/Discriminator -> Saves model weights.

### `evaluate_imputer.py`
**Responsibility**: Validation script to measure imputation quality.
*   **Metrics**: Calculates RMSE, MAE, and KS-Test scores to compare imputed values against ground truth.
*   **Output**: Generates visualization plots in `docs/evaluation_plots`.

### `inference.py`
**Responsibility**: The production pipeline for healing real-world data gaps.
*   **Key Functions**: `run_imputation()`
*   **Process**: Loads Raw Data + Anomaly Report -> Prepares Features -> Runs Neural Imputation -> Applies Physics Post-processing.

### `requirements.txt`
**Responsibility**: Lists external dependencies.
*   **Key Libraries**: `torch`, `pandas`, `numpy`, `scikit-learn`.

## 2. Source Code (`can-imputer/src/`)

### `gain.py`
**Responsibility**: Defines the Neural Network architecture.
*   **Key Classes**: 
    *   `Generator`: The "Artist" that fills in missing values.
    *   `Discriminator`: The "Critic" that distinguishes real vs. imputed data.

### `trainer.py`
**Responsibility**: Encapsulates the training loop and optimization logic.
*   **Key Class**: `GAINTrainer`
*   **Methods**: `train_step()`, `save_checkpoint()`.

### `preprocessor.py`
**Responsibility**: Handles data normalization and scaling.
*   **Key Class**: `ImputationPreprocessor`
*   **Logic**: Scales data to [0, 1] range for stable neural network training. Use `fit=False` during inference to use saved production boundaries.

### `postprocessor.py`
**Responsibility**: The Physics-Informed layer that runs *after* the neural network.
*   **Key Class**: `NbSPostprocessor`
*   **Logic**: Enforces hard physical limits (e.g., no negative PM2.5), smooths seams between real and imputed data, and checks diurnal consistency.

## 3. Utilities (`can-imputer/src/utils/`)

### `data_loaders.py`
**Responsibility**: PyTorch Dataset definitions.
*   **Key Class**: `NbSDataset`
*   **Logic**: Handles the batching of time-series data and the generation of random masks for training.

### `metrics.py`
**Responsibility**: Mathematical functions for performance evaluation.
*   **Functions**: `rmse_score()`, `mae_score()`, `ks_test_score()`.
