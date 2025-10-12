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

# Calculate tort reform factors
df_premium['tort_reform_factor'] = 1.0
for i, row in df_premium.iterrows():
    year = row['accident_year']
    if year <= 2005:
        df_premium.loc[i, 'tort_reform_factor'] = 0.670
    elif year == 2006:
        df_premium.loc[i, 'tort_reform_factor'] = 0.750
    else:
        df_premium.loc[i, 'tort_reform_factor'] = 1.000

# Load triangle data
df_triangle = pd.read_csv(triangle_data_path)
df_triangle = df_triangle.dropna(how='all')
df_triangle = df_triangle.set_index('Accident Year')

for col in df_triangle.columns:
    df_triangle[col] = df_triangle[col].astype(str).str.replace(',', '').replace('nan', np.nan)
    df_triangle[col] = pd.to_numeric(df_triangle[col], errors='coerce')

### STEP 3: Calculate Adjusted Reported Claims
# Adjust the reported claims for tort reform to bring all years to AY 2008 tort law level

