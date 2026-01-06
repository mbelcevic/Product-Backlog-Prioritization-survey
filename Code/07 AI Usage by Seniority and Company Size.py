import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "FinalResults.xlsx"
xls = pd.ExcelFile(file_path)

# Load the data from the first sheet
df = pd.read_excel(xls, sheet_name="Sheet1")
df = df[df["Participated"]=="Yes"]


# Rename the column for AI usage for clarity
df.rename(columns={"In the last 12 months, have you ever used AI or machine learning tools for product backlog prioritization?": "UsedAI"}, inplace=True)

# Count occurrences of AI usage responses by seniority
ai_usage_counts = df.groupby("Seniority")["UsedAI"].value_counts().unstack()

# Calculate percentages
total_counts = ai_usage_counts.sum(axis=1)  # Total responses per seniority level
percentage_counts = ai_usage_counts.div(total_counts, axis=0) * 100  # Convert to percentages

# Custom color palette
custom_palette = {
    "No, but I am open to trying it": "#08306b",  # Intense Royal Blue
    "Yes, occasionally": "#2171b5",  # Electric Blue
    "Yes, regularly": "#4292c6",  # Bold Teal Blue
    "No, and I am not interested": "#8B0000"  # Dark Red
}

# Create the bar chart
fig, ax = plt.subplots(figsize=(12, 13))  # Increase figure height
bar_width = 0.9  # Make bars wider

# Apply custom colors
ai_usage_counts.plot(
    kind="bar",
    ax=ax,
    width=bar_width,
    edgecolor="black",
    color=[custom_palette[col] if col in custom_palette else "#58C4DD" for col in ai_usage_counts.columns]  # Default fallback color
)

# Add dotted horizontal lines at every 10 units
max_y_value = ai_usage_counts.max().max()  # Get highest bar value
for y in range(10, int(max_y_value) + 10, 10):
    ax.axhline(y=y, linestyle="dotted", color="gray", linewidth=1.2, alpha=0.7)

# Add labels on top of each bar with count and percentage on separate lines
for i, seniority in enumerate(ai_usage_counts.index):
    for j, category in enumerate(ai_usage_counts.columns):
        count = ai_usage_counts.loc[seniority, category]
        percentage = percentage_counts.loc[seniority, category]
        if count > 0:  # Only label bars with values
            ax.text(
                i + j * (bar_width / len(ai_usage_counts.columns)) - (bar_width / 2) + (bar_width / (2 * len(ai_usage_counts.columns))),  # Center text
                count + 1,  # Position above the bar
                f"{count}\n({percentage:.0f}%)",  # Format as "15\n(20%)"
                ha="center",
                fontsize=12,
                fontweight="bold",
                color="black"
            )

# Set labels and title with padding
plt.xlabel("Seniority Level", fontsize=14)
plt.ylabel("Number of Responses", fontsize=14)
plt.title("AI/ML Usage in Product Backlog Prioritization by Seniority Level", fontsize=16, pad=20)  # Added padding
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title="Used AI", bbox_to_anchor=(1, 1), fontsize=12)

# Show the plot
plt.show()

# Load the Excel file
file_path = "FinalResults.xlsx"
xls = pd.ExcelFile(file_path)

# Load the data from the first sheet
df = pd.read_excel(xls, sheet_name="Sheet1")

# Rename the column for AI usage for clarity
df.rename(columns={"In the last 12 months, have you ever used AI or machine learning tools for product backlog prioritization?": "UsedAI"}, inplace=True)

# Count occurrences of AI usage responses by company size
ai_usage_counts = df.groupby("CompanySize")["UsedAI"].value_counts().unstack()

# Calculate percentages
total_counts = ai_usage_counts.sum(axis=1)  # Total responses per company size
percentage_counts = ai_usage_counts.div(total_counts, axis=0) * 100  # Convert to percentages

# Custom color palette
custom_palette = {
    "No, but I am open to trying it": "#08306b",  # Intense Royal Blue
    "Yes, occasionally": "#2171b5",  # Electric Blue
    "Yes, regularly": "#4292c6",  # Bold Teal Blue
    "No, and I am not interested": "#8B0000"  # Dark Red
}

# Create the bar chart
fig, ax = plt.subplots(figsize=(15, 10))  # Increase figure height
bar_width = 1.2  # Adjust bar width for better spacing
bar_spacing = 0.3  # Increase space between groups

# Create positions for the bars
num_categories = len(ai_usage_counts.columns)
x = range(len(ai_usage_counts.index))

# Plot each category separately to introduce spacing
for j, category in enumerate(ai_usage_counts.columns):
    ax.bar(
        [i + j * (bar_width / num_categories) + (bar_spacing * i) for i in x],
        percentage_counts[category],  # Use percentage instead of raw count
        width=bar_width / num_categories,
        label=category,
        edgecolor="black",
        color=custom_palette.get(category, "#58C4DD")
    )

# Add labels on top of each bar with the percentage on one line and the count below
for i, company_size in enumerate(ai_usage_counts.index):
    for j, category in enumerate(ai_usage_counts.columns):
        count = ai_usage_counts.loc[company_size, category]
        percentage = percentage_counts.loc[company_size, category]
        if count > 0:  # Only label bars with values
            ax.text(
                i + j * (bar_width / num_categories) + (bar_spacing * i),  # Adjust position for spacing
                percentage + 1,  # Small offset above the bar
                f"{percentage:.0f}%\n({count})",  # Format as "23%\n(45)"
                ha="center",
                fontsize=9,
                color="black"
            )

# Add dotted horizontal grid lines
ax.yaxis.grid(True, linestyle="dotted", linewidth=0.8, alpha=0.7)  # Dotted grid for better readability
ax.set_axisbelow(True)  # Ensure grid lines are behind bars

# Set labels and title with padding
plt.xlabel("Company Size", fontsize=14)
plt.ylabel("Percentage of Responses", fontsize=14)  # Update Y-axis label
plt.title("AI/ML Usage in Product Backlog Prioritization by Company Size", fontsize=16, pad=20)

# Adjust X-ticks to align with bars
plt.xticks(
    [i + (num_categories - 1) * (bar_width / (2 * num_categories)) + (bar_spacing * i / 2) for i in x],
    ai_usage_counts.index,
    rotation=45,
    fontsize=9
)
plt.yticks(fontsize=12)
plt.legend(title="Used AI", bbox_to_anchor=(1, 1), fontsize=12)

# Show the plot
plt.show()
