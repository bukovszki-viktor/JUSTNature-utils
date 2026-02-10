# SME User Guide

## 1. Quick Start

### Step 1: Generate Sample Data
To test the engine, you first need a dataset. The toolkit includes a generator that creates meaningful synthetic data based on real European city profiles.

```bash
# Generate standard metadata profile
python sample_gen.py
```
*   **Output**: `data/raw/city_metadata.csv`

> **Tip**: You can toggle `schema_type="extended"` in `sample_gen.py` to generate a richer dataset with social vulnerability indices and NO2 levels.

### Step 2: Run the Matchmaker
Execute the main script to process the data and find peers.

```bash
python run_matchmaking.py
```

## 2. Outputs

### A. Terminal Report
The script prints the "Top 1 Match" for every city directly to the console.
```text
[Budapest ] ↔ [Leuven   ] | Alignment: 0.901
[Milan    ] ↔ [Gzira    ] | Alignment: 0.516
```

### B. Similarity Matrix (CSV)
*   **Location**: `data/output/similarity_matrix.csv`
*   **Use Case**: Import into Excel or Python for custom network analysis.

### C. Contextual Heatmap (PNG)
*   **Location**: `docs/similarity_heatmap.png`
*   **Use Case**: High-contrast visual for presentations. Indigo cells indicate strong matches.

## 3. Customizing the Engine
The SME is schema-agnostic. To use your own data:
1.  Replace `data/raw/city_metadata.csv` with your own file.
2.  Ensure it has a `City` column.
3.  The engine will **automatically detect**:
    *   **IUCN Columns**: Any column starting with `IUCN_` (e.g., `IUCN_Criterion_1`).
    *   **Numeric Columns**: Auto-normalized.
    *   **Categorical Columns**: Auto-vectorized (e.g., `NbS_Type`).
