import pandas as pd
from scipy import stats

# 1. LOAD DATA
try:
    df = pd.read_csv('FinalResults.csv')
    # Filter for participants only
    if "Participated" in df.columns:
        df = df[df["Participated"] == "Yes"]
except FileNotFoundError:
    print("Error: 'FinalResults.csv' not found. Please ensure the file is in the working directory.")
    exit()

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

# COMBINED DEMOGRAPHICS LIST
# Format: (Display Name, Column Name in CSV)
demographics = [
    ('Seniority Level', 'Seniority'), 
    ('Company Size', 'CompanySize'),
    ('AI Usage Frequency', 'UsedAI'), 
    ('AI User vs Non-User', 'AIUsage')
]

# 3. RUN TESTS
for method in sat_cols_map.values():
    # Check if the method column actually exists after renaming
    if method not in df.columns:
        continue

    for demo_name, demo_col in demographics:
        # Skip if demographic column missing
        if demo_col not in df.columns:
            continue
            
        # Get data for this method and demographic, dropping NAs
        temp_df = df[[demo_col, method]].dropna()
        
        # Create groups based on unique values in the demographic column
        groups = [temp_df[temp_df[demo_col] == g][method] for g in temp_df[demo_col].unique()]
        groups = [g for g in groups if len(g) > 0]
        
        # Kruskal-Wallis requires at least 2 groups
        if len(groups) < 2: 
            continue
            
        # Run Kruskal-Wallis Test
        stat, p = stats.kruskal(*groups)
        
        # Determine Significance Stars
        sig = 'ns'
        if p < 0.001: sig = '***'
        elif p < 0.01: sig = '**'
        elif p < 0.05: sig = '*'
        
        # specific finding analysis (only if significant)
        finding = "-"
        if p < 0.05:
            # Calculate means to see which group is highest
            means = temp_df.groupby(demo_col)[method].mean().sort_values(ascending=False)
            if not means.empty:
                finding = f"Highest: {means.index[0]} ({means.iloc[0]:.2f})"
            
        results.append({
            'Method (Satisfaction)': method,
            'Demographic Factor': demo_name,
            'Test Statistic (H)': f"{stat:.2f}",
            'df': len(groups) - 1,
            'P-Value': p,  # Keep as float for sorting/formatting later
            'Sig.': sig,
            'Finding': finding
        })

# 4. FORMAT & EXPORT
if results:
    res_df = pd.DataFrame(results)
    
    # Sort for better readability
    res_df = res_df.sort_values(by=['Method (Satisfaction)', 'Demographic Factor'])
    
    # Format P-Value column for report (Use < .001 notation)
    res_df['P-Value'] = res_df['P-Value'].apply(lambda x: "< .001" if x < 0.001 else f"{x:.3f}")

    # EXPORT TO CSV
    output_filename = 'Appendix_B_Satisfaction_Combined.csv'
    res_df.to_csv(output_filename, index=False)
    
    print(f"Success! Combined satisfaction analysis saved to '{output_filename}'")
    print("-" * 30)
    print(res_df.head().to_markdown(index=False))
else:
    print("No results were generated. Please check your data columns and content.")