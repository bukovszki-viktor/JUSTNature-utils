# Environmental SEM Analysis Tool

## Overview
This tool performs a Structural Equation Model (SEM) analysis using the `semopy` library. It validates psychological pathways driving environmental intention and impact based on survey data (Huang et al., 2021). The tool employs a "Double Trimming" method to refine both measurement indicators and structural paths for small sample sizes.

## Prerequisites
- Python 3.8+
- The dependencies listed in `requirements.txt`

## Installation
1. Clone the repository or navigate to the `SEM` directory.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Ensure your input data is placed in `data/Szombathely_data.xlsx`.
2. Run the analysis script from the `src` directory:
   ```bash
   python src/sem.py
   ```
   Or from the root:
   ```bash
   python src/sem.py
   ```
3. Check the `output/` directory for results.

## Input Data Format
The tool expects an Excel file (`Szombathely_data.xlsx`) with specific headers mapped to constructs:
- **ER**: Individual Responsibility
- **EC**: Environmental Concern
- **SEK**: Subjective Environmental Knowledge
- **ATB**: Attitude Towards Behavior
- **SN**: Subjective Norms (Social Pressure)
- **PBC**: Perceived Behavioral Control
- **BI**: Behavioral Intention
- **PB**: Pro-environmental Behavior

## Methodology
### 1. Data Preparation
- Loads raw survey data and cleans numeric columns.
- Performs fuzzy matching to map survey questions to constructs.
- Handles reverse-coded items (e.g., "authorities are responsible").

### 2. Model Estimation
- **Full Model**: Fits the initial theoretical model with all indicators and paths.
- **Double Trimming**:
    - **Measurement Trimming**: Removes non-significant indicators (p >= 0.05) to improve construct reliability, keeping the first indicator as a reference.
    - **Structural Trimming**: Removes non-significant causal paths from the structural model.
- **Final Model**: Re-fits the trimmed model and reports statistical fit indices (CFI, RMSEA).

### 3. Output
- **Console**: Detailed logs of mapping, trimming decisions, and fit comparison.
- **File**: `output/SEM_Cleaned_Dataset.xlsx` (Cleaned data used for SEM).
- **Report**: `output/SEM_Impact_Report.md` (Markdown report with path analysis, measurement reliability, and fit metrics).
