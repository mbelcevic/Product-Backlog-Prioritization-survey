import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Load data
file_path = "FinalResults.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")
df = df[df["Participated"]=="Yes"]

# Function to categorize AI users
def AIyes(x):
    return "AI User" if "Yes" in str(x) else "Not AI User"

df["UserOrNot"] = df["UsedAI"].apply(AIyes)

# List of prioritization methods
satisfaction_columns = [
    "MoSCoW (Must-have, Should-have, Could-have, Won’t-have)",
    "RICE (Reach, Impact, Confidence, Effort)",
    "WSJF (Weighted Shortest Job First)",
    "Value vs. Effort Matrix",
    "Cost of Delay",
    "Opportunity Scoring",
    "Custom Formula",
    "Critical Path",
]

# Map long method names to short names
short_names = {
    "MoSCoW (Must-have, Should-have, Could-have, Won’t-have)": "MoSCoW",
    "RICE (Reach, Impact, Confidence, Effort)": "RICE",
    "WSJF (Weighted Shortest Job First)": "WSJF",
    "Value vs. Effort Matrix": "Value-Effort",
    "Cost of Delay": "Cost-Delay",
    "Opportunity Scoring": "Opp-Scoring",
    "Custom Formula": "Custom-Formula",
    "Critical Path": "Critical-Path",
}

# Convert data to long format
df_long = df.melt(
    id_vars=["UserOrNot"],
    value_vars=satisfaction_columns,  # Use actual column names
    var_name="Method",
    value_name="Satisfaction"
)

# Rename methods using short names
df_long["Method"] = df_long["Method"].map(short_names)

# Remove rows where Method is NaN (in case any are missing from the mapping)
df_long = df_long.dropna(subset=["Method"])

# Create box plot
plt.figure(figsize=(12, 6))
sns.boxplot(
    x="Method",
    y="Satisfaction",
    hue="UserOrNot",
    data=df_long,
    palette={"AI User": "#011F4B", "Not AI User": "#4292c6"},
      medianprops={"color": "red", "alpha": 1},
      boxprops={"alpha": 0.5}
)
plt.xticks(rotation=45, ha="right")
plt.title("Satisfaction Scores by Prioritization Method: AI vs. Non-AI Users")
plt.xlabel("Prioritization Method")
plt.ylabel("Satisfaction Score")
plt.legend(title="User Group", loc="upper left", bbox_to_anchor=(1, 1))
plt.show()
