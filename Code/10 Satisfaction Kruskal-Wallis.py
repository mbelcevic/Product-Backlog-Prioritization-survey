import pandas as pd
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

# 3. RUN TESTS
for method in sat_cols_map.values():
    for demo_name, demo_col in demographics:
        temp_df = df[[demo_col, method]].dropna()
        groups = [temp_df[temp_df[demo_col]==g][method] for g in temp_df[demo_col].unique()]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) < 2: continue
            
        stat, p = stats.kruskal(*groups)
        
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
            'Finding': finding
        })

# 4. FORMAT & EXPORT
res_df = pd.DataFrame(results)
res_df = res_df.sort_values(by=['Method (Satisfaction)', 'Demographic Factor'])
res_df['P-Value'] = res_df['P-Value'].apply(lambda x: "< .001" if x < 0.001 else f"{x:.3f}")

# EXPORT TO CSV
output_filename = 'Appendix_B_Satisfaction.csv'
res_df.to_csv(output_filename, index=False)
print(f"Success! Satisfaction analysis saved to '{output_filename}'")
print(res_df.head().to_markdown(index=False))