import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import os
import warnings
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def run_complete_did_workflow(input_file):
    """
    Step 1: Data Cleaning & Preparation
    Dual aggregation: Broad Modules + Keyword-Specific Focus Areas
    """
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found at {input_file}.")
        return

    print("--- Phase 1: Cleaning Data & Multi-Tier Mapping ---")
    # Load the Excel file - targeted at Sheet1
    df = pd.read_excel(input_file, sheet_name='Sheet1', header=2)
    df.columns = [str(col).strip() for col in df.columns]
    
    # EXCLUSION: Remove Dési from the entire dataset
    df = df[~df['Location'].str.lower().str.contains('dési', na=False)].copy()
    
    # Define Treatment and Control Groups
    treatment_sites = [
        'százhold park', 
        'károly gáspár tér', 
        'szent istván park',
        'zrínyi ilona általános iskola'
    ]
    
    def define_treatment(loc):
        loc_str = str(loc).lower()
        if 'control' in loc_str or 'kontroll' in loc_str:
            return 0
        if any(site in loc_str for site in treatment_sites):
            return 1
        return 0

    df['treat'] = df['Location'].apply(define_treatment)
    
    if 'Before/after' in df.columns:
        df['post'] = df['Before/after'].str.lower().map({'before': 0, 'after': 1})
    
    def to_numeric_safe(val):
        if pd.isna(val): return np.nan
        val_str = str(val).lower().strip()
        if val_str in ['n/a', 'nan', '', 'nincs adat']: return np.nan
        try: return float(val)
        except: return np.nan

    # Clean numeric outcomes
    outcome_candidates = df.columns[11:]
    for col in outcome_candidates:
        df[col] = df[col].apply(to_numeric_safe)

    df = df.copy()

    # --- INDICATOR MAPPING ---
    print("\n[Validation Log: Indicator Aggregation]")

    # A. Broad Module Indicators (Index-based)
    # Satisfaction Index (approx columns 11-39)
    df['score_satisfaction'] = df.iloc[:, 11:39].mean(axis=1, skipna=True)
    # Knowledge/Awareness Index (approx columns 42-62)
    df['score_knowledge'] = df.iloc[:, 42:82].mean(axis=1, skipna=True)
    # Social Capital Index (approx columns 120+)
    df['score_social'] = df.iloc[:, 136:172].mean(axis=1, skipna=True)
    
    print(f" - Broad Indicators calculated: satisfaction, knowledge, social.")

    # Detailed Validation Log for Broad Indicators
    print(f" - Satisfaction KPI (cols 11-38): '{df.columns[11]}' ... '{df.columns[38]}'")
    print(f" - Knowledge KPI (cols 42-81): '{df.columns[42]}' ... '{df.columns[81]}'")
    print(f" - Social KPI (cols 136-end): '{df.columns[136]}' ... '{df.columns[171]}'")

    # B. Keyword Focus Indicators (Predefined Keywords)
    # Use lowercase matching to ensure we catch all columns regardless of capitalization
    all_cols_lower = [c.lower() for c in df.columns]
    
    # 1. Satisfaction FOCUS
    sat_focus_items = [
        'overall satisfaction', 
        'clean air', 
        'shade', 
        'biodiversity', 
        'vibrance'
    ]
    found_sat_f = [df.columns[i] for i, col in enumerate(all_cols_lower) if any(item in col for item in sat_focus_items)]
    df['score_satisfaction_focus'] = df[found_sat_f].mean(axis=1, skipna=True)
    
    # 2. Awareness FOCUS
    aw_focus_items = [
        'Nature-based Solutions',
        'heat island',
        'nature-based',
        'nature based'
        ]
    found_aw_f = [df.columns[i] for i, col in enumerate(all_cols_lower) if any(item in col for item in aw_focus_items)]
    df['score_awareness_focus'] = df[found_aw_f].mean(axis=1, skipna=True)
    
    # 3. Social Cohesion FOCUS
    social_focus_items = [
        'participation',
        'trust people'
    ]
    found_soc_f = [df.columns[i] for i, col in enumerate(all_cols_lower) if any(item in col for item in social_focus_items)]
    df['score_social_focus'] = df[found_soc_f].mean(axis=1, skipna=True)

    print(f" - Focus Indicators calculated: satisfaction_focus, awareness_focus, social_focus.")
    print(f"   (Focus satisfaction using: {found_sat_f})")
    print(f"   (Focus awareness using: {found_aw_f})")
    print(f"   (Focus social using: {found_soc_f})")

    # Handle Categorical Controls
    df['Gender'] = df['Gender'].fillna('Unknown').astype(str)
    df['Age'] = df['Age'].fillna('Unknown').astype(str)

    # Save Cleaned Data
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_xlsx = os.path.join(output_dir, "Cleaned_Szombathely_Data_Final.xlsx")
    df.to_excel(output_xlsx, index=False)
    print(f"\nSuccess: Cleaned data saved as {output_xlsx}\n")

    """
    Step 2: Visualization
    """
    print("--- Phase 2: Generating Trend Visualizations ---")
    outcomes_to_plot = ['score_satisfaction_focus', 'score_awareness_focus', 'score_social_focus']
    plot_df = df.dropna(subset=['treat', 'post'])
    
    fig, axes = plt.subplots(1, len(outcomes_to_plot), figsize=(20, 5))
    for i, outcome in enumerate(outcomes_to_plot):
        summary = plot_df.groupby(['treat', 'post'])[outcome].mean().reset_index()
        sns.lineplot(data=summary, x='post', y=outcome, hue='treat', marker='o', 
                     palette={0: '#4831D4', 1: '#CCF381'}, ax=axes[i], linewidth=2.5)
        
        axes[i].set_title(f"Focus: {outcome.replace('score_', '').replace('_', ' ').title()}")
        axes[i].set_xticks([0, 1])
        axes[i].set_xticklabels(['Pre', 'Post'])
        axes[i].set_ylabel("Mean Score")
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "did_trends_focus.png"))
    plt.show()

    # 2.2 Plot Broad Module Indicators
    broad_outcomes = ['score_satisfaction', 'score_knowledge', 'score_social']
    fig2, axes2 = plt.subplots(1, 3, figsize=(20, 5))
    for i, outcome in enumerate(broad_outcomes):
        summary = plot_df.groupby(['treat', 'post'])[outcome].mean().reset_index()
        sns.lineplot(data=summary, x='post', y=outcome, hue='treat', marker='s', 
                     palette={0: '#4831D4', 1: '#CCF381'}, ax=axes2[i], linewidth=2.5)
        axes2[i].set_title(f"Broad: {outcome.replace('score_', '').capitalize()}")
        axes2[i].set_xticks([0, 1])
        axes2[i].set_xticklabels(['Pre', 'Post'])
        axes2[i].grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "did_trends_broad.png"))
    print(" - Saved: did_trends_broad.png")
    
    plt.show()

    """
    Step 3: Statistical Regression & Detailed Reporting
    """
    print("\n--- Phase 3: Statistical Inference & Reporting ---")
    
    all_outcomes = [
        'score_satisfaction', 'score_knowledge', 'score_social',
        'score_satisfaction_focus', 'score_awareness_focus', 'score_social_focus'
    ]
    
    final_results = []
    for outcome in all_outcomes:
        formula = f"{outcome} ~ treat * post + C(Gender) + C(Age)"
        try:
            analysis_df = df.dropna(subset=[outcome, 'treat', 'post', 'Gender', 'Age'])
            if len(analysis_df) < 5: continue
            
            model = smf.ols(formula=formula, data=analysis_df).fit()
            term = 'treat:post'
            
            final_results.append({
                'Indicator': outcome,
                'Effect': model.params.get(term, 0),
                'PValue': model.pvalues.get(term, 1.0),
                'N': len(analysis_df)
            })
        except Exception as e:
            print(f"Regression error for {outcome}: {e}")

    # Generate Markdown Report
    report = f"""# Szombathely JUSTNature DiD Comparison Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 1. Indicator Summary (Broad vs. Focus)
This table compares the broad thematic aggregations against the specific keyword-based focus areas.

| Indicator | Causal Effect | P-Value | Significant? |
| :--- | :--- | :--- | :--- |
"""
    for res in final_results:
        sig = "✅ YES" if res['PValue'] < 0.05 else "No"
        report += f"| {res['Indicator']} | {res['Effect']:.4f} | {res['PValue']:.4f} | {sig} |\n"

    with open(os.path.join(output_dir, "DiD_Comparison_Report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Success: Comparative report generated as '{os.path.join(output_dir, 'DiD_Comparison_Report.md')}'")

if __name__ == "__main__":
    # Determine the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct path to data file relative to script location
    data_path = os.path.join(script_dir, "..", "data", "Szombathely_data.xlsx")
    
    run_complete_did_workflow(data_path)