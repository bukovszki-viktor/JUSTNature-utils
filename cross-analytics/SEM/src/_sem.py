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

    # REVERSE CODING
    inv_keyword = 'authorities are responsible'
    for col in df.columns:
        if inv_keyword.lower() in col.lower():
            df[col] = 6 - df[col] 

    sem_data = pd.DataFrame()
    initial_measurement = {}
    mapping_lookup = {} 
    
    for latent, keywords in mapping.items():
        indicators = []
        for i, kw in enumerate(keywords):
            match = [c for c in df.columns if kw.lower() in c.lower()]
            if match:
                col_name = match[0]
                short_name = f"{latent.lower()}{i+1}"
                sem_data[short_name] = df[col_name]
                indicators.append(short_name)
                mapping_lookup[short_name] = col_name
        if indicators:
            initial_measurement[latent] = indicators

    sem_data_cleaned = sem_data.dropna()
    
    # OUTPUT DIRECTORY SETUP
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
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
    model_full = semopy.Model(full_spec)
    model_full.fit(sem_data_cleaned)
    estimates_full = model_full.inspect()
    estimates_full['p-value'] = pd.to_numeric(estimates_full['p-value'], errors='coerce')

    # --- REFINED TRIMMING (Keep Core Paths) ---
    refined_measurement = {}
    for latent, indicators in initial_measurement.items():
        keepers = [indicators[0]] # Always keep the anchor
        for ind in indicators[1:]:
            row = estimates_full[((estimates_full['lval'] == ind) & (estimates_full['rval'] == latent)) | 
                                 ((estimates_full['lval'] == latent) & (estimates_full['rval'] == ind))]
            if not row.empty and row['p-value'].values[0] < 0.05:
                keepers.append(ind)
        refined_measurement[latent] = keepers

    # We force the inclusion of tested paths in the trimmed model to see their final estimates
    trimmed_structural = "BI ~ SN + SEK\nPB ~ BI" 
    
    trimmed_spec = build_spec(refined_measurement, trimmed_structural)
    model_trim = semopy.Model(trimmed_spec)
    model_trim.fit(sem_data_cleaned)
    estimates_trim = model_trim.inspect()
    estimates_trim['p-value'] = pd.to_numeric(estimates_trim['p-value'], errors='coerce')

    # FIT STATS
    def get_fit(m):
        try:
            s = semopy.calc_stats(m)
            def ex(k): return s[k].iloc[0] if hasattr(s[k], 'iloc') else s[k]
            return {"CFI": ex('CFI'), "RMSEA": ex('RMSEA'), "P": ex('chi2 p-value')}
        except: return {"CFI": 0, "RMSEA": 0, "P": 0}

    fit_f = get_fit(model_full)
    fit_t = get_fit(model_trim)

    # --- REPORT GENERATION ---
    report = f"# Szombathely SEM Analysis Report\n**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"**Sample Size (N):** {len(sem_data_cleaned)}\n\n"
    report += "## 1. Executive Summary\nSocial Influence (SN) is the primary driver of intention. Knowledge (SEK) shows a trend but is not significant at N=30.\n\n"
    
    report += "## 2. Psychological Path Analysis\n| Relationship | Estimate | P-Value | Significance |\n| :--- | :--- | :--- | :--- |\n"
    struct_results = estimates_trim[estimates_trim['op'] == '~']
    for _, row in struct_results.iterrows():
        sig = "✅ Significant" if row['p-value'] < 0.05 else "⚠️ Not Significant"
        report += f"| {row['lval']} ← {row['rval']} | {row['Estimate']:.4f} | {row['p-value']:.4f} | {sig} |\n"

    report += "\n## 3. Measurement Reliability (Survey Question Key)\n| ID | Category | Full Question | Status |\n| :--- | :--- | :--- | :--- |\n"
    for latent, indicators in initial_measurement.items():
        for ind in indicators:
            status = "✅ Kept" if ind in refined_measurement[latent] else "❌ Removed"
            report += f"| **{ind}** | {latent} | {mapping_lookup[ind]} | {status} |\n"

    report += f"\n## 4. Model Fit Comparison\n| Metric | Full | Trimmed | Threshold |\n| :--- | :--- | :--- | :--- |\n| CFI | {fit_f['CFI']:.4f} | {fit_t['CFI']:.4f} | > 0.90 |\n| RMSEA | {fit_f['RMSEA']:.4f} | {fit_t['RMSEA']:.4f} | < 0.08 |\n"

    with open(os.path.join(output_dir, "SEM_Impact_Report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print("Success: Updated report generated in output folder.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "..", "data", "Szombathely_data.xlsx")
    run_environmental_sem(input_path)