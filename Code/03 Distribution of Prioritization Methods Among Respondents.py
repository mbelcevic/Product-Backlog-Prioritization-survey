import pandas as pd
import matplotlib.pyplot as plt
import ast

# 1. DEFINE THE MISSING FUNCTION
# This was missing in your snippet, causing the "else:" error
def shorten_method_name(method):
    # Add specific shortening rules here if needed, for example:
    # if method == "Very Long Method Name":
    #     return "Short Name"
    return method

# Load the Excel file
file_path = "FinalResults.xlsx"
xls = pd.ExcelFile(file_path)

# Load the data from the sheet
df = pd.read_excel(xls, sheet_name="Sheet1")
df = df[df["Participated"]=="Yes"]

# Extract and count occurrences of each prioritization method
method_counts = {}
for methods in df["PrioritizationMethodsUsed_Split"].dropna():
    method_list = ast.literal_eval(methods)  # Convert string representation of list to actual list
    for method in method_list:
        method_counts[method] = method_counts.get(method, 0) + 1

# Sort methods by count
sorted_methods = sorted(method_counts.items(), key=lambda x: x[1], reverse=True)
methods, counts = zip(*sorted_methods)

# Calculate total number of respondents
total_respondents = len(df)

# Convert counts to percentages
percentages = [(count / total_respondents) * 100 for count in counts]

# Apply the shortening function
shortened_methods = [shorten_method_name(method) for method in methods]

# Define the bluish high-contrast palette
bluish_palette_high_contrast = [
    "#011F4B", "#03396C", "#005B96", "#007CC3", "#00A6FB",
    "#58C4DD", "#A1E3FF", "#D3F3FF", "#021024", "#042A5B",
    "#0082A9", "#B2F7EF"
]

# Assign colors cyclically in case there are more bars than colors
colors = bluish_palette_high_contrast[:len(shortened_methods)]

# Create horizontal bar chart with the specified color palette
fig, ax = plt.subplots(figsize=(20, 10))
bars = ax.barh(shortened_methods, percentages, color=colors)

# Add text annotations inside the bars
for bar, count, percentage in zip(bars, counts, percentages):
    ax.text(percentage + 1, bar.get_y() + bar.get_height()/2, f"{count} ({percentage:.1f}%)", va='center', fontsize=10)

ax.set_xlabel("Percentage of Respondents (%)")
ax.set_ylabel("Prioritization Method")
ax.set_title("Usage of Prioritization Methods Among Respondents")
ax.set_xlim(0, max(percentages) + 5)  # Adjust x-axis limits for better spacing
ax.invert_yaxis()  # Invert y-axis to have the most used method on top

plt.show()