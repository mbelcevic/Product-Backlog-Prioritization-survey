import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
#from collections import Counter
#from matplotlib.ticker import MultipleLocator

# Load data
data_str = "FinalResults.xlsx"
df = pd.read_excel(data_str, engine="openpyxl")
df = df[df["Participated"]=="Yes"]

# Selecting only the columns related to prioritization methods
methods_columns = [
    "MoSCoW (Must-have, Should-have, Could-have, Won’t-have)",
    "RICE (Reach, Impact, Confidence, Effort)",
    "WSJF (Weighted Shortest Job First)",
    "Value vs. Effort Matrix",
    "Kano Model",
    "Eisenhower Matrix",
    "Cost of Delay"
]

# Creating a dictionary where the column names are keys and values are non-null values
methods_dict = {
    col: df[col].dropna().tolist() for col in methods_columns
}

# Display the resulting dictionary
methods_dict

listaVrednosti= [value for _, value in methods_dict.items()]
listaLabela = [key for key, _ in methods_dict.items()]

import matplotlib.pyplot as plt

# Define scientific blue shades
colors = [
    "#1f77b4",  # Science Blue
    "#377eb8",  # Sky Blue
    "#4c72b0",  # Deep Blue
    "#6baed6",  # Light Blue
    "#2171b5",  # Dark Blue
    "#08306b",  # Midnight Blue
    "#4292c6"   # Cyan Blue
]

# Function to shorten method names by removing text after "("
def shorten_method_name(method):
    return method.split(" (")[0]  # Keep only text before "("


# Create a mapping of old names to shortened names
renamed_methods = {col: shorten_method_name(col) for col in methods_columns}

# Apply renaming to method labels
listaLabela = [renamed_methods[label] for label in listaLabela]


# Create a prettier box plot with shortened names
fig, ax = plt.subplots(figsize=(10, 6))
box = ax.boxplot(methods_dict.values(), patch_artist=True, tick_labels=listaLabela)  # Use renamed labels

# Style the box plot
for patch, color in zip(box["boxes"], colors):
    patch.set(facecolor=color, alpha=0.6)  # Fill box with blue shades

# Set titles and labels
ax.set_title("Distribution of Prioritization Method Ratings", fontsize=14, fontweight="bold")
ax.set_xlabel("Prioritization Methods", fontsize=12)
ax.set_ylabel("Scores", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.6)

# Rotate x-axis labels for better readability
plt.xticks(rotation=30, ha="right")

# Show the plot
plt.show()


