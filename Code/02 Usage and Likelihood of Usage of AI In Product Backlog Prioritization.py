import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "FinalResults.xlsx"
xls = pd.ExcelFile(file_path)

# Load the sheet into a DataFrame
df = pd.read_excel(xls, sheet_name='Sheet1')
df = df[df["Participated"]=="Yes"]

# Define the color palette
bluish_palette_high_contrast = [
    "#011F4B", "#03396C", "#005B96", "#007CC3",
    "#00A6FB", "#58C4DD", "#A1E3FF", "#D3F3FF"
]


# Function to create a percentage bar chart with count labels
def create_percentage_bar_chart(data, title, xlabel, ylabel, color_palette):
    plt.figure(figsize=(10, 6))

    # Calculate percentages
    value_counts = data.value_counts(normalize=True) * 100
    absolute_counts = data.value_counts()

    ax = value_counts.plot(kind='bar', color=color_palette[:len(value_counts)])

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add labels on top of the bars
    for i, (count, pct) in enumerate(zip(absolute_counts, value_counts)):
        ax.text(i, pct + 1, f"{count} ({pct:.1f}%)", ha='center', fontsize=10)

    # Adjust y-axis limit to prevent text from going out
    ax.set_ylim(0, value_counts.max() + 5)  # Adding 5% padding

    plt.show()

# Create bar charts for AI usage and likelihood of use
create_percentage_bar_chart(df['UsedAI'], "Usage of AI in Product Backlog Prioritization", "Usage", "Percentage (%)", bluish_palette_high_contrast)
create_percentage_bar_chart(df['LikelihoodUseAI'], "Likelihood to Use AI in Future", "Likelihood", "Percentage (%)", bluish_palette_high_contrast)
