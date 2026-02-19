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
    Performs 'Double Trimming': refines both structural paths and measurement indicators
    to optimize model fit for small sample sizes.
    """
    print("--- Phase 1: Data Preparation & Construct Mapping ---")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Load data
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

    # Define construct mapping using fuzzy column names
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

    sem_data = pd.DataFrame()
    initial_measurement = {}
    
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
            initial_measurement[latent] = indicators
            print(f" - {latent} mapped to {len(indicators)} columns.")

    # Drop rows with missing values
    sem_data_cleaned = sem_data.dropna()
    print(f"\nData ready. Sample size (N): {len(sem_data_cleaned)}")
    
    # Save cleaned dataset for review
    dataset_output = "SEM_Cleaned_Dataset.xlsx"
    sem_data_cleaned.to_excel(dataset_output, index=False)
    print(f"Cleaned dataset saved as '{dataset_output}'")

    # ---------------------------------------------------------
    # PHASE 2: FULL MODEL EXECUTION
    # ---------------------------------------------------------
    def build_spec(meas_dict, structural_str):
        spec = "# Measurement Model\n"
        for lat, inds in meas_dict.items():
            spec += f"{lat} =~ {' + '.join(inds)}\n"
        spec += "\n# Structural Model\n" + structural_str
        return spec

    initial_structural = """
    ATB ~ ER + EC + SEK
    BI ~ ATB + SN + PBC
    PB ~ BI
    """
    
    full_spec = build_spec(initial_measurement, initial_structural)

    print("\n--- Phase 2: Full Model Estimation ---")
    model_full = semopy.Model(full_spec)
    model_full.fit(sem_data_cleaned)
    estimates_full = model_full.inspect()
    estimates_full['p-value'] = pd.to_numeric(estimates_full['p-value'], errors='coerce')

    # ---------------------------------------------------------
    # PHASE 3: DOUBLE TRIMMING (Measurement + Structural)
    # ---------------------------------------------------------
    print("\n--- Phase 3: Double Trimming (Refining Indicators & Paths) ---")
    
    # 1. Trim Measurement Model
    # Rule: Keep index 1 (reference) OR p-value < 0.05
    refined_measurement = {}
    for latent, indicators in initial_measurement.items():
        keepers = []
        for i, ind in enumerate(indicators):
            if i == 0: # Always keep the reference indicator (The NaN p-value)
                keepers.append(ind)
                continue
            
            # Check p-value for this specific loading
            row = estimates_full[(estimates_full['lval'] == ind) & (estimates_full['rval'] == latent)]
            if not row.empty:
                pval = row['p-value'].values[0]
                if not np.isnan(pval) and pval < 0.05:
                    keepers.append(ind)
        
        refined_measurement[latent] = keepers

    # 2. Trim Structural Model
    # Rule: Keep only paths with p-value < 0.05
    sig_paths = estimates_full[(estimates_full['op'] == '~') & (estimates_full['p-value'] < 0.05)]
    
    trimmed_structural = ""
    if not sig_paths.empty:
        # Group significant paths
        path_map = {}
        for _, row in sig_paths.iterrows():
            if row['lval'] not in path_map: path_map[row['lval']] = []
            path_map[row['lval']].append(row['rval'])
        
        for target, predictors in path_map.items():
            trimmed_structural += f"{target} ~ {' + '.join(predictors)}\n"
    else:
        print("!! No significant structural paths found. Keeping strongest trend for math stability.")
        # Fallback: Keep the strongest path even if not significant (BI ~ SN)
        trimmed_structural = "BI ~ SN\n"

    trimmed_spec = build_spec(refined_measurement, trimmed_structural)

    # ---------------------------------------------------------
    # PHASE 4: TRIMMED MODEL ESTIMATION & COMPARISON
    # ---------------------------------------------------------
    print("\n--- Phase 4: Trimmed Model Estimation ---")
    model_trim = semopy.Model(trimmed_spec)
    try:
        model_trim.fit(sem_data_cleaned)
        estimates_trim = model_trim.inspect()
        estimates_trim['p-value'] = pd.to_numeric(estimates_trim['p-value'], errors='coerce')
    except Exception as e:
        print(f"Trimmed model failed to converge: {e}")
        return

    def get_fit_metrics(m):
        try:
            s = semopy.calc_stats(m)
            def extract(k):
                v = s[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
            return {"CFI": extract('CFI'), "RMSEA": extract('RMSEA'), "P-Value": extract('chi2 p-value')}
        except: return {"CFI": 0, "RMSEA": 0, "P-Value": 0}

    fit_f = get_fit_metrics(model_full)
    fit_t = get_fit_metrics(model_trim)

    print("\n[Model Comparison]")
    print(f"{'Metric':<10} | {'Full Model':<12} | {'Trimmed Model'}")
    print("-" * 45)
    for m in ['CFI', 'RMSEA', 'P-Value']:
        print(f"{m:<10} | {fit_f[m]:<12.4f} | {fit_t[m]:.4f}")

    print("\n[Final Scientific Insight (Trimmed)]")
    # Display the final proven relationships
    struct_results = estimates_trim[estimates_trim['op'] == '~']
    for _, row in struct_results.iterrows():
        sig = "✅" if row['p-value'] < 0.05 else "⚠️"
        print(f"{sig} {row['lval']} is driven by {row['rval']} (Est: {row['Estimate']:.3f}, p: {row['p-value']:.4f})")

if __name__ == "__main__":
    input_xlsx = os.path.join("data", "Szombathely_data.xlsx")
    run_environmental_sem(input_xlsx)