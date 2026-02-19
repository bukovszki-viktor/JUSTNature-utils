import pandas as pd
import numpy as np
import semopy
import os
import warnings

# Suppress technical warnings for cleaner output
warnings.filterwarnings("ignore")

def run_environmental_sem(file_path):
    """
    Executes a Structural Equation Model (SEM) based on the Huang et al. (2021) study.
    Uses survey items from the 'Attitude' section to model psychological pathways.
    """
    print("--- Phase 1: Data Preparation & Construct Mapping ---")
    
    # Load data
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    df = pd.read_excel(file_path, sheet_name='Sheet1', header=2)
    df.columns = [str(col).strip() for col in df.columns]
    
    # Exclude Dési from dataset as per project requirements
    df = df[~df['Location'].str.lower().str.contains('dési', na=False)].copy()

    def to_numeric(val):
        try:
            v = str(val).lower().strip()
            if v in ['n/a', 'nan', '', 'nincs adat']: return np.nan
            return float(val)
        except: return np.nan

    # Clean the numeric parts of the survey
    for col in df.columns[11:]:
        df[col] = df[col].apply(to_numeric)

    # Define construct mapping using fuzzy column names from the provided survey items
    mapping = {
        'ER': ['Every member of the public should accept responsibility', 
               'The authorities are responsible for the environment',
               'conscious behaviors of individuals are significant'],
        'EC': ['interferences with nature often produce disastrous', 
               'balance of nature is delicate', 
               'human beings are severely abusing', 
               'worried about the environment'],
        'SEK': ['knowledge and skills to behave pro-environmentally', 
                'several ways to participate, protect, create', 
                'aware of specific problems of my cities'],
        'ATB': ['eco-friendly behavior is a good way for solving', 
                'useful to behave pro-environmentally', 
                'wise to conserve energy'],
        'SN': ['people who are important to me think', 
               'important to me want me to be environmentally', 
               'social pressure to preserve the environment'],
        'PBC': ['find it easy to be friendly with the environment', 
                'capable of adopting eco-friendly behaviors', 
                'Being friendly with the environment is in my hands', 
                'confident that I can protect the environment'],
        'BI': ['reduce my carbon footprint in the forthcoming months', 
               'intend to engage in behaviors to protect', 
               'plan to stop wasting natural resources'],
        'PB': ['participated in policy consultations', 
               'participated in volunteer activities', 
               'sort glass or tins or plastic']
    }

    # Extract and rename columns for semopy syntax
    sem_data = pd.DataFrame()
    model_spec = "\n# Measurement Model\n"
    
    # Log found columns for validation
    print("\n[Mapping Discovery]")
    for latent, keywords in mapping.items():
        indicators = []
        for i, kw in enumerate(keywords):
            match = [c for c in df.columns if kw.lower() in c.lower()]
            if match:
                col_name = match[0]
                short_name = f"{latent.lower()}{i+1}"
                sem_data[short_name] = df[col_name]
                indicators.append(short_name)
        
        if indicators:
            model_spec += f"{latent} =~ {' + '.join(indicators)}\n"
            print(f" - {latent} mapped to {len(indicators)} columns.")

    # Define Structural Model (The Paths)
    model_spec += """
# Structural Model (Paths from Huang et al. 2021)
ATB ~ ER + EC + SEK
BI ~ ATB + SN + PBC
PB ~ BI
"""

    # Drop rows with missing values for the SEM
    sem_data_cleaned = sem_data.dropna()
    print(f"\nData ready for SEM. Sample size (N) after cleaning: {len(sem_data_cleaned)}")

    # SAVE FUNCTION: Export the cleaned dataset for review
    dataset_output = "SEM_Cleaned_Dataset.xlsx"
    sem_data_cleaned.to_excel(dataset_output, index=False)
    print(f"Success: Cleaned SEM dataset saved for review as '{dataset_output}'")

    if len(sem_data_cleaned) < 20:
        print("Warning: Sample size is extremely small for SEM. Results may be unstable.")

    print("\n--- Phase 2: Model Estimation ---")
    model = semopy.Model(model_spec)
    model.fit(sem_data_cleaned)
    
    # Inspect estimates
    estimates = model.inspect()
    
    # Convert p-value to numeric safely
    estimates['p-value'] = pd.to_numeric(estimates['p-value'], errors='coerce')
    
    print("\n--- Phase 3: Psychological Path Analysis ---")
    # Filter for structural paths (regression)
    paths = estimates[(estimates['op'] == '~')]
    
    print(f"{'Path':<15} | {'Estimate':<10} | {'P-Value':<10} | {'Status'}")
    print("-" * 55)
    for _, row in paths.iterrows():
        path_name = f"{row['lval']} ~ {row['rval']}"
        est = row['Estimate']
        pval = row['p-value']
        
        # Determine status string
        if np.isnan(pval):
            status = "Fixed/Reference"
        else:
            status = "✅ SIGNIFICANT" if pval < 0.05 else "Non-significant"
            
        print(f"{path_name:<15} | {est:<10.4f} | {pval:<10.4f} | {status}")

    print("\n--- Phase 4: Model Fit Indices ---")
    try:
        stats = semopy.calc_stats(model)
        
        # Safely extract scalar values from the results series/dataframe
        def get_stat(key):
            val = stats[key]
            if hasattr(val, 'iloc'):
                return val.iloc[0]
            return val

        chi2_p = get_stat('chi2 p-value')
        cfi = get_stat('CFI')
        rmsea = get_stat('RMSEA')
        
        print(f"Chi-square p-value: {chi2_p:.4f}")
        print(f"CFI (Target > 0.9): {cfi:.4f}")
        print(f"RMSEA (Target < 0.08): {rmsea:.4f}")
    except Exception as e:
        print(f"Could not calculate all fit indices: {e}")
    
    # Recommendation Logic
    print("\n[Scientific Insight]")
    # Check for the SN -> BI path specifically
    sn_path = estimates[(estimates['lval'] == 'BI') & (estimates['rval'] == 'SN')]
    if not sn_path.empty:
        pval = sn_path['p-value'].values[0]
        if not np.isnan(pval) and pval < 0.05:
            print("- Social Influence (Subjective Norms) is the primary driver of intention.")
            print("  Recommendation: Focus on community visibility and peer-to-peer environmental norms.")
    
    # Check for the Intention -> Behavior path
    b_path = estimates[(estimates['lval'] == 'PB') & (estimates['rval'] == 'BI')]
    if not b_path.empty:
        pval = b_path['p-value'].values[0]
        if not np.isnan(pval) and pval < 0.05:
            print("- Behavioral Intention Successfully translates to Actual Participation.")
        else:
            print("- High intentions are not translating into actual behavior (p > 0.05).")
            print("  Recommendation: Identify physical or logistical barriers preventing action.")

if __name__ == "__main__":
    # Ensure the data file path matches your project structure
    input_xlsx = os.path.join("data", "Szombathely_data.xlsx")
    try:
        run_environmental_sem(input_xlsx)
    except Exception as e:
        print(f"Error executing SEM: {e}")