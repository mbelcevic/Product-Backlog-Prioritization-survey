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

# Collect and count all methods by seniority
methods_per_seniority = {}
total_per_seniority = {}

for seniority in df['Seniority'].unique():
    methods_list = df[df['Seniority'] == seniority]['PrioritizationMethodsUsed'].dropna()
    all_methods = []
    total_per_seniority[seniority] = len(methods_list)
    for methods_str in methods_list:
        all_methods.extend(split_methods(methods_str))
    methods_per_seniority[seniority] = Counter(all_methods)

# Find top 5 most common methods
top = 5
all_methods = sum((methods_per_seniority[sen] for sen in methods_per_seniority), Counter())
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
method_usage_percentage = pd.DataFrame(index=['Junior', 'Medior', 'Senior'])
for method in top_5_methods:
    short_method = short_names.get(method, method)
    method_usage_percentage[short_method] = [
        (methods_per_seniority['Junior'].get(method, 0) / total_per_seniority['Junior']) * 100,
        (methods_per_seniority['Medior'].get(method, 0) / total_per_seniority['Medior']) * 100,
        (methods_per_seniority['Senior'].get(method, 0) / total_per_seniority['Senior']) * 100
    ]

# Define bluish high-contrast palette
bluish_palette_high_contrast = [
    "#00A6FB", "#B2F7EF", "#021024", "#FFC0CB", "#964B00"
]

# Plot grouped bar chart
ax = method_usage_percentage.plot(kind='bar', figsize=(12, 8), width=0.8, color=bluish_palette_high_contrast[:len(top_5_methods)])
plt.title('Distribution of Methods by Experience Level')
plt.ylabel('Percentage of Users (%)')
plt.xticks(rotation=0)
plt.legend(title='Methods')
plt.tight_layout()

# Set Y-axis with step of 5
ax.yaxis.set_major_locator(MultipleLocator(5))

for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', label_type='edge', padding=3)

plt.show()