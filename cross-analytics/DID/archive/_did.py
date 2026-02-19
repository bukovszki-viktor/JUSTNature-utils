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
    Based on JUSTNature WP3 Guidelines for Humanities Indicators
    """
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found at {input_file}.")
        return

    print("--- Phase 1: Cleaning Data (WP3 Guidelines Alignment) ---")
    # Load the Excel file - targeted at Sheet1
    df = pd.read_excel(input_file, sheet_name='Sheet1', header=2)
    df.columns = [str(col).strip() for col in df.columns]
    
    # Defragment the dataframe early to avoid PerformanceWarnings
    df = df.copy()
    
    # Define Treatment and Control Groups
    # Added 'dési' to the treatment list as per latest instructions
    treatment_sites = [
        'százhold park', 
        'károly gáspár tér', 
        'szent istván park',
        'zrínyi ilona általános iskola',
        'dési'
    ]
    
    def define_treatment(loc):
        loc_str = str(loc).lower()
        if 'control' in loc_str or 'kontroll' in loc_str:
            return 0
        # Check if any of the treatment keywords are in the location name
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

    # Outcomes usually start after metadata (Index 11)
    outcome_cols = df.columns[11:]
    for col in outcome_cols:
        df[col] = df[col].apply(to_numeric_safe)

    df = df.copy()

    # --- INDICATOR MAPPING (JUSTNature WP3 Pillar Construction) ---
    
    # Satisfaction Index (approx columns 11-39)
    df['score_satisfaction'] = df.iloc[:, 11:39].mean(axis=1, skipna=True)
    
    # Knowledge Index (approx columns 42-62)
    df['score_knowledge'] = df.iloc[:, 42:62].mean(axis=1, skipna=True)
    
    # Attitudes Index
    att_cols = [c for c in df.columns if any(word in c for word in ['Attitude', 'Environmental', 'ATB', 'Civic'])]
    if att_cols:
        df['score_attitudes'] = df[att_cols].mean(axis=1, skipna=True)
    else:
        df['score_attitudes'] = df.iloc[:, 85:110].mean(axis=1, skipna=True)

    # Social Capital Index
    social_cols = [c for c in df.columns if any(word in c.lower() for word in ['trust', 'reciprocity', 'justification'])]
    if social_cols:
        df['score_social'] = df[social_cols].mean(axis=1, skipna=True)
    else:
        df['score_social'] = df.iloc[:, 120:].mean(axis=1, skipna=True)

    # Handle Categorical Controls
    df['Gender'] = df['Gender'].fillna('Unknown').astype(str)
    df['Age'] = df['Age'].fillna('Unknown').astype(str)

    # Save Cleaned Data
    output_xlsx = "Cleaned_Szombathely_Data_Final.xlsx"
    df.to_excel(output_xlsx, index=False)
    print(f"Success: Cleaned data saved as {output_xlsx}\n")

    """
    Step 2: Visualization
    """
    print("--- Phase 2: Generating Trend Visualizations ---")
    outcomes_to_plot = ['score_satisfaction', 'score_knowledge', 'score_social', 'score_attitudes']
    plot_df = df.dropna(subset=['treat', 'post'])
    
    fig, axes = plt.subplots(1, len(outcomes_to_plot), figsize=(22, 5))
    for i, outcome in enumerate(outcomes_to_plot):
        if outcome not in df.columns: continue
        summary = plot_df.groupby(['treat', 'post'])[outcome].mean().reset_index()
        
        sns.lineplot(data=summary, x='post', y=outcome, hue='treat', marker='o', 
                     palette={0: '#7f8c8d', 1: '#2980b9'}, ax=axes[i], linewidth=2.5)
        
        axes[i].set_title(f"WP3 Trend: {outcome.replace('score_', '').capitalize()}")
        axes[i].set_xticks([0, 1])
        axes[i].set_xticklabels(['Pre', 'Post'])
        axes[i].set_ylabel("Mean Score")
        axes[i].legend(['Control', 'Treatment (incl. Dési)'])
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("did_trends.png")
    plt.show()

    """
    Step 3: Statistical Regression & Dynamic Reporting
    """
    print("\n--- Phase 3: Statistical Inference & Dynamic Reporting ---")
    
    final_stats = []
    analysis_outcomes = ['score_satisfaction', 'score_knowledge', 'score_social', 'score_attitudes']
    
    for outcome in analysis_outcomes:
        # The 'treat:post' interaction term is our Causal Effect
        formula = f"{outcome} ~ treat * post + C(Gender) + C(Age)"
        try:
            analysis_df = df.dropna(subset=[outcome, 'treat', 'post', 'Gender', 'Age'])
            if len(analysis_df) < 5: continue
            
            model = smf.ols(formula=formula, data=analysis_df).fit()
            
            term = 'treat:post'
            final_stats.append({
                'Outcome': outcome.replace('score_', '').capitalize(),
                'Effect': model.params.get(term, 0),
                'StdErr': model.bse.get(term, 0),
                'Tstat': model.tvalues.get(term, 0),
                'PValue': model.pvalues.get(term, 1.0),
                'N': len(analysis_df)
            })
        except Exception as e:
            print(f"Error analyzing {outcome}: {e}")

    # Generate the Markdown Report
    report_content = f"""# Szombathely JUSTNature WP3 Impact Report
**Methodology: Difference-in-Differences (DiD) on Humanities Indicators**
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 1. Methodology Summary
This analysis adheres to the **JUSTNature WP3 Guidelines**. We evaluate the causal impact of nature-based solutions using a DiD approach. This run includes **Százhold park** and **Dési** as treatment sites. To ensure robustness against changes in survey respondent demographics, the model controls for **Gender** and **Age**.

## 2. Indicator Impact Summary
| WP3 Indicator | Causal Effect ($\beta_3$) | Std. Error | t-stat | P-Value | Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for s in final_stats:
        sig_marker = "✅ Significant" if s['PValue'] < 0.05 else "Non-significant"
        report_content += f"| {s['Outcome']} | {s['Effect']:.4f} | {s['StdErr']:.4f} | {s['Tstat']:.2f} | {s['PValue']:.4f} | {sig_marker} |\n"

    report_content += "\n## 3. Dynamic Narrative Analysis\n"
    for s in final_stats:
        if s['PValue'] < 0.05:
            direction = "positive" if s['Effect'] > 0 else "negative"
            report_content += f"- **{s['Outcome']}**: Found a statistically significant {direction} causal effect ({s['Effect']:.4f}). This confirms the intervention successfully impacted this indicator.\n"
        else:
            report_content += f"- **{s['Outcome']}**: No statistically significant treatment effect detected (P={s['PValue']:.4f}).\n"

    with open("DiD_WP3_Impact_Report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("Success: WP3 aligned report generated as 'DiD_WP3_Impact_Report.md'")

if __name__ == "__main__":
    # Path configuration
    file_path = os.path.join("data", "Szombathely_data.xlsx")
    run_complete_did_workflow(file_path)