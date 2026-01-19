import pandas as pd
import numpy as np
from scipy import stats


# 1. LOAD DATA

df = pd.read_csv('FinalResults.csv')
df = df[df["Participated"]=="Yes"]

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

# --- HELPER FUNCTIONS ---

def calculate_cramers_v(ct):
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    if min_dim <= 0:
        return 0.0
    chi2 = stats.chi2_contingency(ct)[0]
    return np.sqrt(chi2 / (n * min_dim))

def bootstrap_cramers_v(series1, series2, n_boots=1000):
    
    # Create a clean dataframe for these two columns
    data = pd.DataFrame({'d': series1, 'm': series2}).dropna()
    n = len(data)
    
    if n == 0:
        return 0.0, 0.0, 0.0

    # 1. Point Estimate
    ct_orig = pd.crosstab(data['d'], data['m'])
    v_point = calculate_cramers_v(ct_orig)

    # 2. Bootstrap Distribution
    boot_vals = []
    values = data.values  # Convert to numpy for slightly better speed
    
    for _ in range(n_boots):
        # Resample with replacement
        indices = np.random.randint(0, n, n)
        sample = values[indices]
        
        # Create temp Crosstab
        # Note: We use pandas crosstab to ensure handling of categorical alignment
        ct_boot = pd.crosstab(sample[:, 0], sample[:, 1])
        
        v_boot = calculate_cramers_v(ct_boot)
        boot_vals.append(v_boot)
    
    # 3. Percentiles (95% CI)
    ci_low = np.percentile(boot_vals, 2.5)
    ci_high = np.percentile(boot_vals, 97.5)
    
    return v_point, ci_low, ci_high

# 3. RUN TESTS
for m_short, m_long in methods_map.items():
    # Create Binary Usage Column
    df[f'{m_short}_Used'] = df['PrioritizationMethodsUsed'].fillna('').apply(lambda x: m_long in x)
    
    for demo_name, demo_col in demographics:
        # Prepare Data
        demo_series = df[demo_col]
        usage_series = df[f'{m_short}_Used']
        
        # Calculate Stats & CI
        v, ci_low, ci_high = bootstrap_cramers_v(demo_series, usage_series, n_boots=1000)
        
        # Run standard Chi2 for p-value
        ct = pd.crosstab(demo_series, usage_series)
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        min_dim = min(ct.shape) - 1
        
        # Determine Significance Stars
        sig = 'ns'
        if p < 0.001: sig = '***'
        elif p < 0.01: sig = '**'
        elif p < 0.05: sig = '*'
        
        results.append({
            'Method': m_short,
            'Demographic Factor': demo_name,
            'χ²': f"{chi2:.2f}",
            'df': dof,
            'Effect Size (V)': f"{v:.2f}",
            '95% CI': f"[{ci_low:.2f}, {ci_high:.2f}]", # NEW COLUMN
            'df*': min_dim,
            'P-Value': p,
            'Sig.': sig
        })

# 4. FORMAT & EXPORT
res_df = pd.DataFrame(results)

# Sort
res_df = res_df.sort_values(by=['Method', 'Demographic Factor'])

# Format P-Value
res_df['P-Value'] = res_df['P-Value'].apply(lambda x: "< .001" if x < 0.001 else f"{x:.3f}")

# EXPORT
output_filename = 'Appendix_A_Adoption_with_CIs.csv'
res_df.to_csv(output_filename, index=False)

print(res_df[['Method', 'Demographic Factor', 'Effect Size (V)', '95% CI', 'Sig.']].head().to_markdown(index=False))
