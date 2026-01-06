import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter
from matplotlib.ticker import MultipleLocator

# Load data
data_str = "FinalResults.xlsx"
df = pd.read_excel(data_str, engine="openpyxl")
df = df[df["Participated"]=="Yes"]

# Function to split methods
def split_methods(methods):
    return re.split(r",\s*(?![^()]*\))", methods)

# Function to categorize company sizes
def categorize_company_size(size):
    maximumSize = 0
    if isinstance(size, str):
        size = size.replace(",", "")  # Remove commas if present
        numbers = [int(s) for s in re.findall(r"\d+", size)]  # Extract numeric values
        if numbers:
            maximumSize = max(numbers)
        else:
            return "Unknown"

    if maximumSize <= 200:
        return "1 to 200"
    elif maximumSize <= 1000:
        return "201 to 1000"
    elif maximumSize <= 10000 and len(numbers) != 1:
        return "1001 to 10000"
    else:
        return "over 10000"

# Apply categorization
df['CompanySizeCategory'] = df['CompanySize'].apply(categorize_company_size)

# Collect and count all methods by company size category
methods_per_company_size = {}
total_per_company_size = {}

for company_size in df['CompanySizeCategory'].unique():
    methods_list = df[df['CompanySizeCategory'] == company_size]['PrioritizationMethodsUsed'].dropna()
    all_methods = []
    total_per_company_size[company_size] = len(methods_list)
    for methods_str in methods_list:
        all_methods.extend(split_methods(methods_str))
    methods_per_company_size[company_size] = Counter(all_methods)

# Find top 5 most common methods
top = 5
all_methods = sum((methods_per_company_size[size] for size in methods_per_company_size), Counter())
top_5_methods = [m[0] for m in all_methods.most_common(top)]

# Map long method names to short names
short_names = {
    "MoSCoW (Must-have, Should-have, Could-have, Won’t-have)": "MoSCoW",
    "RICE (Reach, Impact, Confidence, Effort)": "RICE",
    "WSJF (Weighted Shortest Job First)": "WSJF",
    "Value vs. Effort Matrix": "Value-Effort",
    "Kano Model": "Kano"
}

# Prepare data for chart
method_usage_percentage = pd.DataFrame(index=['1 to 200', '201 to 1000', '1001 to 10000', 'over 10000'])
for method in top_5_methods:
    short_method = short_names.get(method, method)
    method_usage_percentage[short_method] = [
        (methods_per_company_size.get(size, {}).get(method, 0) / total_per_company_size.get(size, 1)) * 100
        for size in ['1 to 200', '201 to 1000', '1001 to 10000', 'over 10000']
    ]

# Define bluish high-contrast palette
bluish_palette_high_contrast = [
   "#0A0A0A", "#00A6FB", "#B2F7EF", "#D3F3FF", "#03396C"
]

# Plot grouped bar chart
ax = method_usage_percentage.plot(kind='bar', figsize=(12, 6), width=0.9, color=bluish_palette_high_contrast[:len(top_5_methods)])
plt.title('Prioritization Method Usage by Company Size')
plt.ylabel('Percentage of Users (%)')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Methods')
plt.tight_layout()

# Set Y-axis with step of 5
ax.yaxis.set_major_locator(MultipleLocator(5))

for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', label_type='edge', padding=3)

plt.show()
