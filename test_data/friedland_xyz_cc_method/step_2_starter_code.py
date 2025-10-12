import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

# Data file paths
triangle_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/reported_claims_triangle.csv'
premium_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/earned_premium.csv'
rate_changes_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/rate_changes.csv'
claim_ratio_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/expected_claim_ratio.csv'

# Load premium and rate changes
df_premium = pd.read_csv(premium_data_path)
df_premium['earned_premium'] = df_premium['earned_premium'].astype(str).str.replace(',', '').str.replace('"', '')
df_premium['earned_premium'] = pd.to_numeric(df_premium['earned_premium'], errors='coerce')

df_rate_changes = pd.read_csv(rate_changes_data_path)
df_rate_changes['rate_changes'] = df_rate_changes['rate_changes'].astype(str).str.replace('%', '')
df_rate_changes['rate_changes'] = pd.to_numeric(df_rate_changes['rate_changes'], errors='coerce') / 100
df_rate_changes['rate_changes'] = df_rate_changes['rate_changes'].fillna(0)

# Calculate cumulative rate factors
df_premium['cumulative_rate_factor'] = 1.0
for i in range(len(df_premium)):
    if i == 0:
        df_premium.loc[i, 'cumulative_rate_factor'] = 1.0
    else:
        df_premium.loc[i, 'cumulative_rate_factor'] = df_premium.loc[i-1, 'cumulative_rate_factor'] * (1 + df_rate_changes.loc[i, 'rate_changes'])

# Calculate on-level factors and current level earned premium
latest_cumulative = df_premium.iloc[-1]['cumulative_rate_factor']
df_premium['on_level_factor'] = latest_cumulative / df_premium['cumulative_rate_factor']
df_premium['current_level_earned_premium'] = df_premium['earned_premium'] * df_premium['on_level_factor']

### STEP 2: Calculate Tort Reform On-Level Factors
# Calculate the tort reform adjustment factors to bring all years to AY 2008 tort law level

