import pandas as pd
import numpy as np
from scipy import stats

# 1. LOAD DATA
df = pd.read_csv('FinalResults.csv')
df = df[df["Participated"]=="Yes"]

# 2. CONFIGURATION
sat_cols_map = {
    'MoSCoW (Must-have, Should-have, Could-have, Won’t-have)': 'MoSCoW',
    'RICE (Reach, Impact, Confidence, Effort)': 'RICE',
    'WSJF (Weighted Shortest Job First)': 'WSJF',
    'Value vs. Effort Matrix': 'Value vs. Effort',
    'Kano Model': 'Kano Model',
    'Eisenhower Matrix': 'Eisenhower Matrix',
    'Cost of Delay': 'Cost of Delay',
    'Opportunity Scoring': 'Opportunity Scoring',
    'Custom Formula': 'Custom Formula',
    'Critical Path': 'Critical Path'
}
df.rename(columns=sat_cols_map, inplace=True)

results = []
demographics = [('AI Usage Frequency', 'UsedAI'), ('AI User vs Non-User', 'AIUsage')]

# Bootstrap settings
n_boot = 1000 
rng = np.random.default_rng(42)

# 3. RUN TESTS
for method in sat_cols_map.values():
    for demo_name, demo_col in demographics:
        if demo_col not in df.columns:
            continue
            
        temp_df = df[[demo_col, method]].dropna()
        n = len(temp_df)
        
        unique_vals = temp_df[demo_col].unique()
        groups = [temp_df[temp_df[demo_col]==g][method] for g in unique_vals]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) < 2: 
            continue
            
        stat, p = stats.kruskal(*groups)
        
        # Effect Size (Epsilon-squared)
        epsilon2 = stat * (n + 1) / (n**2 - 1)
        
        # Bootstrap
        boot_vals = []
        for _ in range(n_boot):
            resamp = temp_df.sample(n=n, replace=True)
            bgroups = [resamp[resamp[demo_col]==g][method] for g in resamp[demo_col].unique()]
            bgroups = [g for g in bgroups if len(g) > 0]
            if len(bgroups) < 2:
                continue
            try:
                bstat, _ = stats.kruskal(*bgroups)
                b_eps = bstat * (n + 1) / (n**2 - 1)
                boot_vals.append(b_eps)
            except ValueError:
                pass
        
        # Format CI as single string
        ci_str = "-"
        if len(boot_vals) > 0:
            ci_lower = np.percentile(boot_vals, 2.5)
            ci_upper = np.percentile(boot_vals, 97.5)
            ci_str = f"[{ci_lower:.3f}, {ci_upper:.3f}]"
        
        sig = 'ns'
        if p < 0.001: sig = '***'
        elif p < 0.01: sig = '**'
        elif p < 0.05: sig = '*'
        
        finding = "-"
        if p < 0.05:
            means = temp_df.groupby(demo_col)[method].mean().sort_values(ascending=False)
            finding = f"Highest: {means.index[0]} ({means.iloc[0]:.2f})"
            
        results.append({
            'Method (Satisfaction)': method,
            'Demographic Factor': demo_name,
            'Test Statistic (H)': f"{stat:.2f}",
            'df': len(groups) - 1,
            'P-Value': p,
            'Sig.': sig,
            'Effect Size (eps^2)': epsilon2,
            '95% CI': ci_str,
            'Finding': finding
        })

# 4. FORMAT & EXPORT
res_df = pd.DataFrame(results)
if not res_df.empty:
    res_df = res_df.sort_values(by=['Method (Satisfaction)', 'Demographic Factor'])
    
    # Format float columns
    res_df['Effect Size (eps^2)'] = res_df['Effect Size (eps^2)'].map('{:.3f}'.format)
    
    output_filename = 'TableA3_Satisfaction-AI_Usage_Combined_CI.csv'
    res_df.to_csv(output_filename, index=False)
    print(res_df.head().to_markdown(index=False))
