import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_rel

# Load the dataset from the uploaded file
df = pd.read_csv("research_summary.txt", sep="\t")

# Conversion factor from pixel to degrees
conversion_factor = 0.068055

# Convert PRL and SD values from pixels to degrees
df["PRLx_deg"] = df["PRLx"] * conversion_factor
df["PRLy_deg"] = df["PRLy"] * conversion_factor
df["PRLx_sd_deg"] = df["PRLx_sd"] * conversion_factor
df["PRLy_sd_deg"] = df["PRLy_sd"] * conversion_factor

# Compute BCEA in deg² assuming rho = 0
df["BCEA_deg2"] = 2 * np.pi * df["PRLx_sd_deg"] * df["PRLy_sd_deg"]

# Parameters to analyze
parameters = {
    "Sacc_N": "Numero saccadi",
    "Sacc_Amp": "Ampiezza saccadi (deg)",
    "Sacc_Dur": "Durata saccadi (s)",
    "Sacc_PV": "Peak velocity saccadi",
    "Fix_Dur": "Durata fissazioni (s)",
    "PRLx_deg": "PRLx (deg)",
    "PRLy_deg": "PRLy (deg)",
    "PRLx_sd_deg": "Deviazione PRLx (deg)",
    "PRLy_sd_deg": "Deviazione PRLy (deg)",
    "BCEA_deg2": "BCEA (deg²)"
}

# Prepare dataframe for paired t-tests
grouped = df.groupby(["NAME", "TASK", "CONDITION"]).mean(numeric_only=True).reset_index()
pivoted = grouped.pivot(index=["NAME", "TASK"], columns="CONDITION")

# Perform paired t-tests
ttest_results = []
for task in df["TASK"].unique():
    for param, label in parameters.items():
        try:
            nv = pivoted.loc[(slice(None), task), (param, "NV")].dropna()
            bm = pivoted.loc[(slice(None), task), (param, "BM")].dropna()
            common_idx = nv.index.intersection(bm.index)
            t_stat, p_val = ttest_rel(nv.loc[common_idx], bm.loc[common_idx])
            ttest_results.append({
                "Task": task,
                "Parametro": label,
                "p-value (t-test)": round(p_val, 5)
            })
        except Exception:
            ttest_results.append({
                "Task": task,
                "Parametro": label,
                "p-value (t-test)": np.nan
            })

# Create summary table
ttest_df = pd.DataFrame(ttest_results)
ttest_df_pivot = ttest_df.pivot(index="Task", columns="Parametro", values="p-value (t-test)")
ttest_df.to_csv("paired_ttest_summary.csv", index=False)

# Plotting high-resolution boxplots
sns.set(style="whitegrid", font_scale=1.2)
for param, label in parameters.items():
    plt.figure(figsize=(10, 6), dpi=300)
    sns.boxplot(data=df, x="TASK", y=param, hue="CONDITION", palette="Set2")
    plt.title(f"{label} per Task e Condizione")
    plt.ylabel(label)
    plt.xlabel("Task")
    plt.legend(title="Condizione")
    plt.tight_layout()
    plt.savefig(f"boxplot_{param}.png")
    plt.close()

# Generate heatmap of p-values
plt.figure(figsize=(12, 6), dpi=300)
sns.heatmap(ttest_df_pivot, annot=True, cmap="coolwarm_r", cbar_kws={'label': 'p-value'}, linewidths=0.5)
plt.title("Heatmap dei p-value (paired t-test) per ciascun parametro e task")
plt.tight_layout()
plt.savefig("heatmap_paired_ttest.png")
plt.close()

