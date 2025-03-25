import pandas as pd
from scipy.stats import chi2_contingency

df = pd.read_csv("data/processed/ataxia_api_results.csv")

# Compute counts
true_positives = sum(df["API_Flag"] == 1)
false_negatives = sum(df["API_Flag"] == 0)
uncertain = sum(df["API_Flag"] == 2)
total = len(df)

print(f"Total genes tested: {total}")
print(f"Correctly flagged (TP): {true_positives} ({(true_positives / total) * 100:.2f}%)")
print(f"Incorrectly flagged as not ataxia-related (FN): {false_negatives} ({(false_negatives / total) * 100:.2f}%)")
print(f"Uncertain classifications: {uncertain} ({(uncertain / total) * 100:.2f}%)")

observed = [true_positives, false_negatives, uncertain]
expected = [total, 0, 0]  # Ideally, all should be "Yes"

res = chi2_contingency([observed, expected])

chi2_stat = res.statistic
p_value = res.pvalue
dof = res.dof

print(f"Chi-square statistic: {chi2_stat}")
print(f"P-value: {p_value}")
print(f"Degrees of freedom: {dof}")
