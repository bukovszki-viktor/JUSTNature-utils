# SME Code Reference

This document describes the responsibility of every file in the **Similarity & Matchmaking Engine (SME)** library.

## 1. Root Directory (`sme/`)

### `run_matchmaking.py`
**Responsibility**: The main execution script for the engine.
*   **Key Functions**: `main()`, `plot_similarity_heatmap()`
*   **Process**: Loads metadata -> Vectorizes features -> Calculates Similarity -> Exports Matrix & Heatmap.

### `sample_gen.py`
**Responsibility**: Utility to generate synthetic city metadata for testing.
*   **Key Functions**: `generate_sample()`
*   **Usage**: Creates `data/raw/city_metadata.csv` with either 'standard' or 'extended' schemas.

### `requirements.txt`
**Responsibility**: Lists external dependencies.
*   **Key Libraries**: `pandas`, `numpy`, `scikit-learn`, `matplotlib`.

## 2. Source Code (`sme/src/`)

### `engine.py`
**Responsibility**: Core logic for similarity calculation.
*   **Key Class**: `SMEMatchmaker`
*   **Methods**: 
    *   `build_feature_matrix()`: Normalizes data and handles missing values (Median Imputation).
    *   `calculate_similarity()`: Computes the Cosine Similarity matrix.
    *   `find_top_matches()`: Retrieves peer cities based on alignment scores.

## 3. Utilities (`sme/src/utils/`)

### `vectorizer.py`
**Responsibility**: Handles the transformation of qualitative data into numbers.
*   **Key Class**: `NbSVectorizer`
*   **Logic**: 
    *   **IUCN Scoring**: Maps "Yes/Partial/No" to `[1.0, 0.5, 0.0]`.
    *   **One-Hot Encoding**: Converts categorical types (e.g., `NbS_Type`) into binary vectors.
