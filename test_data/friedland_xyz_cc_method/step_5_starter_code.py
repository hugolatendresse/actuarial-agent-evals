import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

script_dir = Path(__file__).resolve().parent
if "ide_results" in str(script_dir):
    project_root = script_dir.parent.parent.parent
    data_dir = project_root / "test_data" / "friedland_xyz_cc_method"
else:
    data_dir = script_dir
# Data file paths
triangle_data_path = data_dir / 'reported_claims_triangle.csv'
premium_data_path = data_dir / 'earned_premium.csv'
rate_changes_data_path = data_dir / 'rate_changes.csv'
claim_ratio_data_path = data_dir / 'expected_claim_ratio.csv'

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

# Calculate adjusted reported claims for tort reform
latest_reported = df_triangle.ffill(axis=1).iloc[:, -1]
df_premium['reported_claims'] = latest_reported.values
df_premium['adjusted_reported_claims'] = df_premium['reported_claims'] * df_premium['tort_reform_factor']

# Adjust triangle for tort reform
df_triangle_adjusted = df_triangle.copy()
tort_factors_dict = df_premium.set_index('accident_year')['tort_reform_factor'].to_dict()

for idx in df_triangle_adjusted.index:
    year = int(idx)
    factor = tort_factors_dict.get(year, 1.0)
    df_triangle_adjusted.loc[idx] = df_triangle_adjusted.loc[idx] * factor

# Create chainladder triangle from adjusted data
df_long = df_triangle_adjusted.reset_index().melt(
    id_vars=['Accident Year'], 
    var_name='age', 
    value_name='reported'
)
df_long = df_long.dropna()
df_long['age'] = df_long['age'].astype(int)
df_long['Accident Year'] = df_long['Accident Year'].astype(int)
df_long['origin_period'] = pd.PeriodIndex(df_long['Accident Year'].astype(str), freq='Y')
df_long['valuation'] = (df_long['origin_period'] + (df_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

triangle = cl.Triangle(
    df_long, 
    origin='origin_period', 
    development='valuation', 
    columns=['reported'], 
    cumulative=True
)

# Create pipeline with development, tail, and Cape Cod
pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=2)),
    ('tail', cl.TailConstant(tail=1.05)),
    ('cc', cl.CapeCod(trend=0.03425)),
])

# Create sample weight from on-level premium
sample_weight_values = df_premium['current_level_earned_premium'].values.reshape(1, 1, -1, 1)
sample_weight = triangle.copy()
sample_weight.values = sample_weight_values

# Fit the pipeline
pipe.fit(triangle, sample_weight=sample_weight)

# Get Cape Cod model
cc_model = pipe.named_steps.cc

# Get adjusted ultimates
cc_ultimate_adjusted = cc_model.ultimate_

# Adjust back to original tort law level
tort_factors_array = df_premium['tort_reform_factor'].values.reshape(1, 1, -1, 1)
tort_triangle = triangle.copy()
tort_triangle.values = tort_factors_array

cc_ultimate = cc_ultimate_adjusted / tort_triangle
total_cc_ultimate = float(cc_ultimate.sum().sum())

### STEP 5: Calculate Cape Cod IBNR
# Extract IBNR from the Cape Cod model and adjust back to original tort law level

