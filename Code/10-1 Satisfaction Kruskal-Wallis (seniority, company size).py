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
demographics = [('Seniority Level', 'Seniority'), ('Company Size', 'CompanySize')]

def calculate_epsilon_squared(H, n):
    """
    Calculates Epsilon-squared for Kruskal-Wallis.
    Formula: H / ((n^2 - 1) / (n + 1))
    """
    if n <= 1: return 0
    return H / ((n**2 - 1) / (n + 1))

def bootstrap_epsilon_ci(df_subset, group_col, val_col, n_boot=1000, seed=42):
    """
    Bootstraps the CI for Epsilon-squared using stratified resampling.
    """
    np.random.seed(seed)
    boot_es = []
    
    # Group data for stratified resampling
    groups_dict = {g: df_subset[df_subset[group_col] == g] for g in df_subset[group_col].unique()}
    
    for _ in range(n_boot):
        # Stratified resampling: sample each group with replacement
        resampled_parts = []
        for g, data in groups_dict.items():
            resampled_parts.append(data.sample(n=len(data), replace=True))
        
        resampled = pd.concat(resampled_parts)
        
        # Prepare groups for Kruskal-Wallis
        r_groups = [resampled[resampled[group_col]==g][val_col] for g in resampled[group_col].unique()]
        r_groups = [g for g in r_groups if len(g) > 0]
        
        if len(r_groups) < 2:
            continue
            
        try:
            h_stat, _ = stats.kruskal(*r_groups)
            n_total = len(resampled)
            es = calculate_epsilon_squared(h_stat, n_total)
            boot_es.append(es)
        except ValueError:
            continue

    if not boot_es:
        return np.nan, np.nan

    return np.percentile(boot_es, 2.5), np.percentile(boot_es, 97.5)

# 3. RUN TESTS
for method in sat_cols_map.values():
    for demo_name, demo_col in demographics:
        temp_df = df[[demo_col, method]].dropna()
        groups = [temp_df[temp_df[demo_col]==g][method] for g in temp_df[demo_col].unique()]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) < 2: continue
            
        # Standard Kruskal-Wallis Test
        stat, p = stats.kruskal(*groups)
        
        # Calculate Effect Size (Epsilon-squared)
        n_total = len(temp_df)
        epsilon_sq = calculate_epsilon_squared(stat, n_total)
        
        # Calculate Bootstrap CI (95%)
        ci_lower, ci_upper = bootstrap_epsilon_ci(temp_df, demo_col, method)
        
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
            'Epsilon-squared': f"{epsilon_sq:.3f}",
            '95% CI': f"[{ci_lower:.3f}, {ci_upper:.3f}]",
            'Finding': finding
        })

# 4. FORMAT & EXPORT
res_df = pd.DataFrame(results)
res_df = res_df.sort_values(by=['Method (Satisfaction)', 'Demographic Factor'])

print("Analysis Complete. First 5 rows:")
print(res_df.head())

res_df.to_csv('Appendix_A_Table A2', index=False)
