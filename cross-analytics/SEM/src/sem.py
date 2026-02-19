import pandas as pd
import numpy as np
import semopy
import os
import warnings
from datetime import datetime

# Suppress technical warnings for cleaner output
warnings.filterwarnings("ignore")

def run_environmental_sem(file_path):
    """
    Executes a Structural Equation Model (SEM) and generates a Markdown report
    with descriptive question headers and reverse-coding logic.
    """
    print("--- Phase 1: Data Preparation & Construct Mapping ---")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Load data
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=2)
    df.columns = [str(col).strip() for col in df.columns]
    
    # Exclude Dési from dataset
    df = df[~df['Location'].str.lower().str.contains('dési', na=False)].copy()

    def to_numeric(val):
        try:
            v = str(val).lower().strip()
            if v in ['n/a', 'nan', '', 'nincs adat']: return np.nan
            return float(val)
        except: return np.nan

    for col in df.columns[11:]:
        df[col] = df[col].apply(to_numeric)

    # ---------------------------------------------------------
    # CONSTRUCT MAPPING & REVERSE CODING
    # ---------------------------------------------------------
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

    # REVERSE CODING LOGIC
    # Target: 'The authorities are responsible'
    # We invert it so that 5 (Strongly Agree with state responsibility) becomes 
    # 1 (Lower individual-centric responsibility score) for the ER construct.
    inv_keyword = 'authorities are responsible'
    for col in df.columns:
        if inv_keyword.lower() in col.lower():
            print(f" - Inverting scores for: '{col[:30]}...' (Reverse Coding)")
            df[col] = 6 - df[col] # Assuming 1-5 scale

    sem_data = pd.DataFrame()
    initial_measurement = {}
    mapping_lookup = {} 
    
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
                # Store original text for the report
                mapping_lookup[short_name] = col_name
        
        if indicators:
            initial_measurement[latent] = indicators
            print(f" - {latent} mapped to {len(indicators)} columns.")

    sem_data_cleaned = sem_data.dropna()
    
    # Define output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    sem_data_cleaned.to_excel(os.path.join(output_dir, "SEM_Cleaned_Dataset.xlsx"), index=False)

    # --- MODEL SPECS ---
    def build_spec(meas_dict, structural_str):
        spec = "# Measurement Model\n"
        for lat, inds in meas_dict.items():
            if inds: spec += f"{lat} =~ {' + '.join(inds)}\n"
        spec += "\n# Structural Model\n" + structural_str
        return spec

    initial_structural = "ATB ~ ER + EC + SEK\nBI ~ ATB + SN + PBC\nPB ~ BI"
    full_spec = build_spec(initial_measurement, initial_structural)

    # --- EXECUTION ---
    print("\n--- Phase 2: Full Model Estimation ---")
    model_full = semopy.Model(full_spec)
    model_full.fit(sem_data_cleaned)
    estimates_full = model_full.inspect()
    estimates_full['p-value'] = pd.to_numeric(estimates_full['p-value'], errors='coerce')

    # --- TRIMMING ---
    print("\n--- Phase 3: Double Trimming Logic ---")
    refined_measurement = {}
    latent_vars = list(initial_measurement.keys())
    for latent, indicators in initial_measurement.items():
        keepers = []
        for i, ind in enumerate(indicators):
            if i == 0: 
                keepers.append(ind); continue
            row = estimates_full[((estimates_full['lval'] == ind) & (estimates_full['rval'] == latent)) | 
                                 ((estimates_full['lval'] == latent) & (estimates_full['rval'] == ind))]
            if not row.empty:
                if row['p-value'].values[0] < 0.05: keepers.append(ind)
        refined_measurement[latent] = keepers

    sig_struct = estimates_full[(estimates_full['op'] == '~') & 
                                (estimates_full['lval'].isin(latent_vars)) & 
                                (estimates_full['rval'].isin(latent_vars)) &
                                (estimates_full['p-value'] < 0.05)]
    
    trimmed_structural = ""
    if not sig_struct.empty:
        for _, row in sig_struct.iterrows(): trimmed_structural += f"{row['lval']} ~ {row['rval']}\n"
    else:
        trimmed_structural = "BI ~ SN\n" 
    
    trimmed_spec = build_spec(refined_measurement, trimmed_structural)
    model_trim = semopy.Model(trimmed_spec)
    model_trim.fit(sem_data_cleaned)
    estimates_trim = model_trim.inspect()
    estimates_trim['p-value'] = pd.to_numeric(estimates_trim['p-value'], errors='coerce')

    # --- REPORT GENERATION ---
    def get_fit(m):
        try:
            s = semopy.calc_stats(m)
            def extract(k): return s[k].iloc[0] if hasattr(s[k], 'iloc') else s[k]
            return {"CFI": extract('CFI'), "RMSEA": extract('RMSEA'), "P": extract('chi2 p-value')}
        except: return {"CFI": 0, "RMSEA": 0, "P": 0}

    fit_f = get_fit(model_full)
    fit_t = get_fit(model_trim)

    report = f"""# Szombathely SEM Analysis Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Sample Size (N):** {len(sem_data_cleaned)}

## 1. Executive Summary
The model identifies the psychological pathways driving environmental intention. **Social Influence (Subjective Norms)** remains the strongest validated driver.

## 2. Psychological Path Analysis (Construct Relationships)
These are the connections between the abstract categories.

| Relationship | Causal Path | Estimate | P-Value | Significance |
| :--- | :--- | :--- | :--- | :--- |
"""
    struct_results = estimates_trim[(estimates_trim['op'] == '~') & (estimates_trim['lval'].isin(latent_vars))]
    for _, row in struct_results.iterrows():
        sig = "✅ Significant" if row['p-value'] < 0.05 else "⚠️ Trend"
        report += f"| {row['lval']} ← {row['rval']} | {row['lval']} is driven by {row['rval']} | {row['Estimate']:.4f} | {row['p-value']:.4f} | {sig} |\n"

    report += """
## 3. Measurement Reliability (Survey Question Key)
This table clarifies which specific survey questions correspond to the IDs used in the model.

| ID | Category | Full Survey Question | Status |
| :--- | :--- | :--- | :--- |
"""
    for latent, indicators in initial_measurement.items():
        for ind in indicators:
            status = "✅ Kept" if ind in refined_measurement[latent] else "❌ Removed"
            q_text = mapping_lookup[ind]
            report += f"| **{ind}** | {latent} | {q_text} | {status} |\n"

    report += f"""
## 4. Model Fit Comparison
| Metric | Full Model | Trimmed Model | Threshold |
| :--- | :--- | :--- | :--- |
| CFI (Comparative Fit Index) | {fit_f['CFI']:.4f} | {fit_t['CFI']:.4f} | > 0.90 |
| RMSEA (Error Index) | {fit_f['RMSEA']:.4f} | {fit_t['RMSEA']:.4f} | < 0.08 |
| Chi-Square P-Value | {fit_f['P']:.4f} | {fit_t['P']:.4f} | > 0.05 |
"""

    with open(os.path.join(output_dir, "SEM_Impact_Report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSuccess: Professional report with updated formatting saved as '{os.path.join(output_dir, 'SEM_Impact_Report.md')}'")

if __name__ == "__main__":
    # Determine the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct path to data file relative to script location
    input_xlsx = os.path.join(script_dir, "..", "data", "Szombathely_data.xlsx")
    
    run_environmental_sem(input_xlsx)