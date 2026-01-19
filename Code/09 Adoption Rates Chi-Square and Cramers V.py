import pandas as pd
import numpy as np
from scipy import stats

# 1. LOAD DATA
# Make sure your file name matches exactly
df = pd.read_csv('FinalResults.csv')

# 2. CONFIGURATION
methods_map = {
    'MoSCoW': 'MoSCoW',
    'RICE': 'RICE',
    'WSJF': 'WSJF',
    'Value vs. Effort': 'Value vs. Effort Matrix',
    'Kano Model': 'Kano Model',
    'Eisenhower Matrix': 'Eisenhower Matrix',
    'Cost of Delay': 'Cost of Delay',
    'Opportunity Scoring': 'Opportunity Scoring',
    'Custom Formula': 'Custom Formula',
    'Critical Path': 'Critical Path'
}

results = []
demographics = [('Seniority Level', 'Seniority'), ('Company Size', 'CompanySize')]

# 3. RUN TESTS
for m_short, m_long in methods_map.items():
    # Create Binary Usage Column (True/False)
    # This checks if the long method name exists in the respondent's answer
    df[f'{m_short}_Used'] = df['PrioritizationMethodsUsed'].fillna('').apply(lambda x: m_long in x)
    
    for demo_name, demo_col in demographics:
        # Create the Contingency Table (Observed Counts)
        ct = pd.crosstab(df[demo_col], df[f'{m_short}_Used'])
        
        # Run Chi-Square Test
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        
        # Calculate Cramer's V (Effect Size)
        n = ct.sum().sum()
        min_dim = min(ct.shape) - 1  # This is df* (the smaller dimension)
        
        if min_dim > 0:
            v = np.sqrt(chi2 / (n * min_dim))
        else:
            v = 0
        
        # Determine Significance Stars
        sig = 'ns'
        if p < 0.001: sig = '***'
        elif p < 0.01: sig = '**'
        elif p < 0.05: sig = '*'
        
        results.append({
            'Method': m_short,
            'Demographic Factor': demo_name,
            'χ²': f"{chi2:.2f}",
            'df': dof,           # Degrees of Freedom for Chi-Square
            'Effect Size (V)': f"{v:.2f}",
            'df*': min_dim,      # Degrees of Freedom for Cramer's V (New Column!)
            'P-Value': p,
            'Sig.': sig
        })

# 4. FORMAT & EXPORT
res_df = pd.DataFrame(results)

# Sort by Method and Demographic for easier reading
res_df = res_df.sort_values(by=['Method', 'Demographic Factor'])

# Format P-Value for readability
res_df['P-Value'] = res_df['P-Value'].apply(lambda x: "< .001" if x < 0.001 else f"{x:.3f}")

# EXPORT TO CSV
output_filename = 'Appendix_A_Adoption_with_df_star.csv'
res_df.to_csv(output_filename, index=False)

print(f"Success! Adoption analysis saved to '{output_filename}'")
print(res_df.head().to_markdown(index=False))