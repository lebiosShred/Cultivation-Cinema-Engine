import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chisquare

db_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_history.db'
conn = sqlite3.connect(db_path)

query = "SELECT digit_1, digit_2, digit_3 FROM swertres_draws WHERE winning_combination != 'N/A'"
df = pd.read_sql_query(query, conn)
conn.close()

# 1. Total Draws
n_draws = len(df)
print(f"Total Valid Draws Analyzed: {n_draws}")

# 2. Chi-Square Uniformity Test (Are the machines fair?)
# Expected frequency for any digit 0-9 in any position is n_draws / 10
expected = [n_draws / 10.0] * 10
print("\n--- Chi-Square Goodness of Fit ---")
for col in ['digit_1', 'digit_2', 'digit_3']:
    counts = df[col].value_counts().sort_index().values
    chi_stat, p_val = chisquare(counts, f_exp=expected)
    print(f"Position {col}: p-value = {p_val:.4f} (if < 0.05, it's non-uniform)")

# 3. Sum Distribution (Bell Curve Test)
print("\n--- Sum Distribution (Bell Curve) ---")
df['sum'] = df['digit_1'] + df['digit_2'] + df['digit_3']
sum_mean = df['sum'].mean()
sum_std = df['sum'].std()
print(f"Mean Sum: {sum_mean:.2f} (Theoretical expected: 13.5)")
print(f"Standard Deviation: {sum_std:.2f}")

# 4. Birthday Paradox / Repetitions
df['combo'] = df['digit_1'].astype(str) + df['digit_2'].astype(str) + df['digit_3'].astype(str)
combo_counts = df['combo'].value_counts()
unique_combos_seen = len(combo_counts)
print(f"\nUnique combinations seen out of 1000: {unique_combos_seen}")
print(f"Combinations that repeated 3+ times: {len(combo_counts[combo_counts >= 3])}")
print(f"Most drawn combo(s): {combo_counts.index[0]} (Drawn {combo_counts.iloc[0]} times)")

# 5. Coldest Numbers (Never drawn)
missing = 1000 - unique_combos_seen
print(f"Combinations never drawn in 2 years (Coldest): {missing} combinations")
