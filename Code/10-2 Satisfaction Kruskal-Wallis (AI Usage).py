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
# We test both the specific frequency ('UsedAI') and the binary grouping ('AIUsage')
demographics = [('AI Usage Frequency', 'UsedAI'), ('AI User vs Non-User', 'AIUsage')]

# 3. RUN TESTS
for method in sat_cols_map.values():
    for demo_name, demo_col in demographics:
        if demo_col not in df.columns:
            continue
            
        # Get data for this method and demographic
        temp_df = df[[demo_col, method]].dropna()
        
        # Create groups based on unique values in the demographic column
        groups = [temp_df[temp_df[demo_col]==g][method] for g in temp_df[demo_col].unique()]
        groups = [g for g in groups if len(g) > 0]
        
        # Kruskal-Wallis requires at least 2 groups
        if len(groups) < 2: 
            continue
            
        stat, p = stats.kruskal(*groups)
        
        sig = 'ns'
        if p < 0.001: sig = '***'
        elif p < 0.01: sig = '**'
        elif p < 0.05: sig = '*'
        
        finding = "-"
        if p < 0.05:
            # Calculate means to see which group is highest
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
if not res_df.empty:
    res_df = res_df.sort_values(by=['Method (Satisfaction)', 'Demographic Factor'])

    # EXPORT TO CSV
output_filename = 'Appendix_B_Satisfaction-AI_Usage.csv'
res_df.to_csv(output_filename, index=False)
print(f"Success! Satisfaction analysis saved to '{output_filename}'")
print(res_df.head().to_markdown(index=False))

print(res_df)
# res_df.to_csv('Kruskal_Wallis_AI_Satisfaction.csv', index=False)