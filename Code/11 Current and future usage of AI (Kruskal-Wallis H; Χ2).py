import pandas as pd
import numpy as np
from scipy import stats

# 1. LOAD DATA
df = pd.read_csv('FinalResults.csv')
df = df[df["Participated"]=="Yes"]
likelihood_map = {
    'Very unlikely': 1, 'Somewhat unlikely': 2, 'Neutral': 3,
    'Somewhat likely': 4, 'Very likely': 5
}
df['Future_AI_Score'] = df['LikelihoodUseAI'].map(likelihood_map)

results = []
demographics = [('Seniority Level', 'Seniority'), ('Company Size', 'CompanySize')]

# 2. RUN TESTS

# A. Current AI Usage (Chi-Squared)
for demo_name, demo_col in demographics:
    ct = pd.crosstab(df[demo_col], df['UsedAI'])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    
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
        'Key Finding': "Sig. usage patterns" if p < 0.05 else "No diff"
    })

# B. Future Likelihood (Kruskal-Wallis)
for demo_name, demo_col in demographics:
    temp_df = df[[demo_col, 'Future_AI_Score']].dropna()
    groups = [temp_df[temp_df[demo_col]==g]['Future_AI_Score'] for g in temp_df[demo_col].unique()]
    
    stat, p = stats.kruskal(*groups)
    
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
        'df': len(groups) - 1,
        'P-Value': p,
        'Sig.': sig,
        'Key Finding': finding
    })

# 3. FORMAT & EXPORT
res_df = pd.DataFrame(results)
res_df['P-Value'] = res_df['P-Value'].apply(lambda x: "< .001" if x < 0.001 else f"{x:.3f}")

# EXPORT TO CSV
output_filename = 'Appendix_C_AI.csv'
res_df.to_csv(output_filename, index=False)
print(f"Success! AI analysis saved to '{output_filename}'")
print(res_df.to_markdown(index=False))