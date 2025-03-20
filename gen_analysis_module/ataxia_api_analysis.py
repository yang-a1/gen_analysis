import pandas as pd
from scipy.stats import chi2_contingency

# Load the results
df = pd.read_csv("data/processed/ataxia_api_results.csv")

# Compute counts
true_positives = sum(df["API_Flag"] == 1)
false_negatives = sum(df["API_Flag"] == 0)
uncertain = sum(df["API_Flag"] == 2)
total = len(df)

# Print simple accuracy stats
print(f"Total genes tested: {total}")
print(f"Correctly flagged (TP): {true_positives} ({(true_positives / total) * 100:.2f}%)")
print(f"Incorrectly flagged as not ataxia-related (FN): {false_negatives} ({(false_negatives / total) * 100:.2f}%)")
print(f"Uncertain classifications: {uncertain} ({(uncertain / total) * 100:.2f}%)")

# Chi-Square Test (to test if the API is biased toward a specific answer)
observed = [true_positives, false_negatives, uncertain]
expected = [total, 0, 0]  # Ideally, all should be "Yes"

chi2, p, dof, expected_values = chi2_contingency([observed, expected])

print("\nStatistical Analysis:")
print(f"Chi-square value: {chi2:.2f}")
print(f"P-value: {p:.6f} (lower means API is systematically biased)")
