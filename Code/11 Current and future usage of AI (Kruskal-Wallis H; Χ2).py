import pandas as pd
import numpy as np
from scipy import stats

# 1. LOAD DATA
df = pd.read_csv('FinalResults.csv')
df = df[df["Participated"] == "Yes"]

likelihood_map = {
    'Very unlikely': 1, 'Somewhat unlikely': 2, 'Neutral': 3,
    'Somewhat likely': 4, 'Very likely': 5
}
df['Future_AI_Score'] = df['LikelihoodUseAI'].map(likelihood_map)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def cramers_v(x, y):
    """Calculates Cramér's V for two categorical series."""
    confusion_matrix = pd.crosstab(x, y)
    if confusion_matrix.size == 0: return 0
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    if n == 0: return 0
    r, k = confusion_matrix.shape
    return np.sqrt((chi2 / n) / min(k - 1, r - 1))

def epsilon_squared(x, y):
    """Calculates Epsilon-squared for Kruskal-Wallis."""
    # x: categorical group, y: numeric score
    groups = [y[x == g] for g in x.unique()]
    if len(groups) < 2: return 0
    H, _ = stats.kruskal(*groups)
    n = len(y)
    k = len(groups)
    # Unbiased Epsilon-squared formula
    if n == k: return 0
    return (H - k + 1) / (n - k)

def bootstrap_ci(df_subset, col_group, col_target, metric_func, n_boot=1000, ci=0.95):
    """
    Calculates bootstrapped confidence interval for a given metric.
    Uses stratified resampling to preserve group sizes.
    """
    values = []
    for _ in range(n_boot):
        try:
            # Stratified resampling: sample from each group with replacement
            sample = df_subset.groupby(col_group, group_keys=False).apply(lambda x: x.sample(n=len(x), replace=True))
            val = metric_func(sample[col_group], sample[col_target])
            values.append(val)
        except Exception:
            pass # Skip failed iterations (e.g., if a group vanishes, though stratified prevents this)
            
    if not values:
        return "N/A"
        
    lower = np.percentile(values, (1 - ci) / 2 * 100)
    upper = np.percentile(values, (1 + ci) / 2 * 100)
    return f"[{lower:.2f}, {upper:.2f}]"

# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

results = []
demographics = [('Seniority Level', 'Seniority'), ('Company Size', 'CompanySize')]

# A. Current AI Usage (Chi-Squared)
for demo_name, demo_col in demographics:
    temp_df = df[[demo_col, 'UsedAI']].dropna()
    ct = pd.crosstab(temp_df[demo_col], temp_df['UsedAI'])
    
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    stat_val = cramers_v(temp_df[demo_col], temp_df['UsedAI'])
    ci_str = bootstrap_ci(temp_df, demo_col, 'UsedAI', cramers_v)
    
    sig = 'ns'
    if p < 0.001: sig = '***'
    elif p < 0.01: sig = '**'
    elif p < 0.05: sig = '*'
    
    results.append({
        'Survey Question': 'Current AI Usage (Last 12 Months)',
        'Demographic Factor': demo_name,
        'Test Statistic': f"X2={chi2:.2f}",
        'df': dof,
        'P-Value': p,
        'Sig.': sig,
        'Effect Size': f"V={stat_val:.2f}",
        'Effect Size CI (95%)': ci_str,
        'Key Finding': "Sig. usage patterns" if p < 0.05 else "No diff"
    })

# B. Future Likelihood (Kruskal-Wallis)
for demo_name, demo_col in demographics:
    temp_df = df[[demo_col, 'Future_AI_Score']].dropna()
    groups = [temp_df[temp_df[demo_col]==g]['Future_AI_Score'] for g in temp_df[demo_col].unique()]
    
    if len(groups) < 2: continue
        
    stat, p = stats.kruskal(*groups)
    
    # Calculate actual effect size
    n = len(temp_df)
    k = len(groups)
    est_val = (stat - k + 1) / (n - k)
    
    # Calculate CI
    ci_str = bootstrap_ci(temp_df, demo_col, 'Future_AI_Score', epsilon_squared)

    sig = 'ns'
    if p < 0.001: sig = '***'
    elif p < 0.01: sig = '**'
    elif p < 0.05: sig = '*'
    
    finding = "No diff"
    if p < 0.05:
        means = temp_df.groupby(demo_col)['Future_AI_Score'].mean().sort_values(ascending=False)
        finding = f"Highest: {means.index[0]} ({means.iloc[0]:.2f})"

    results.append({
        'Survey Question': 'Future AI Likelihood',
        'Demographic Factor': demo_name,
        'Test Statistic': f"H={stat:.2f}",
        'df': k-1,
        'P-Value': p,
        'Sig.': sig,
        'Effect Size': f"ε²={est_val:.2f}",
        'Effect Size CI (95%)': ci_str,
        'Key Finding': finding
    })

# Save Results
results_df = pd.DataFrame(results)
print(results_df)
results_df.to_csv('Appendix_A_Table A4.csv', index=False)
