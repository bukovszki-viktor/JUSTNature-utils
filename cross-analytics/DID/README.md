# Determine Impact with Difference-in-Differences (DID) Tool

## Overview
This tool performs a Difference-in-Differences (DiD) analysis to evaluate the impact of interventions on various social outcome metrics (Satisfaction, Knowledge, Attitudes, Social Capital). It processes survey data, visualizes trends, and runs statistical regression models to quantify causal effects.

## Prerequisites
- Python 3.8+
- The dependencies listed in `requirements.txt`

## Installation
1. Clone the repository or navigate to the `DID` directory.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Ensure your input data is placed in `data/Szombathely_data.xlsx`.
2. Run the analysis script from the `src` directory:
   ```bash
   python src/did.py
   ```
   Or from the root:
   ```bash
   python src/did.py
   ```
3. Check the `output/` directory for results.

## Input Data Format
The tool expects an Excel file (`Szombathely_data.xlsx`) with a specific structure on 'Sheet1':
- **Header:** The script assumes the actual column headers are on the 3rd row (index 2).
- **Columns:**
    - `Location`: Used to determine Treatment vs Control groups.
    - `Before/after`: Used to distinguish pre- and post-intervention periods.
    - `Gender`, `Age`: Used as covariates in the regression model.
    - **Survey Items:**
        - Satisfaction items (cols 11-39)
        - Knowledge items (cols 42-62)
        - Attitude/Environmental items
        - Social Trust/Reciprocity items

## Methodology
### 1. Data Cleaning
- Loads raw data and strips whitespace from headers.
- **Treatment Assignment:**
    - **Treatment Group:** Locations including 'Százhold park', 'Károly Gáspár tér', 'Szent István park', 'Zrínyi Ilona általános iskola'.
    - **Control Group:** Locations explicitly marked as 'control' or 'kontroll'.
- **Scoring:** Converts Likert scale responses to numeric values and computes composite mean scores for:
    - `score_satisfaction`
    - `score_knowledge`
    - `score_attitudes`
    - `score_social`

### 2. Visualization
- Generates interaction plots (Did Trends) showing the average outcome over time (Pre vs Post) for both Treatment and Control groups.
- These plots help visually inspect the "parallel trends" assumption and the divergence after intervention.

### 3. Statistical Analysis
- Runs an OLS regression model for each outcome:
  $$ Outcome \sim Treatment + Post + (Treatment \times Post) + Gender + Age $$
- **Key Metric:** The coefficient of the interaction term `Treatment:Post` represents the DiD estimator (the causal effect of the intervention).
- Outputs the coefficient and p-value for each outcome.

## Output
- **Console:** statistical summary table.
- **File:** `Cleaned_Szombathely_Data_Final.xlsx` (intermediate cleaned dataset).
- **Plots:** Interactive window displaying trend lines.
