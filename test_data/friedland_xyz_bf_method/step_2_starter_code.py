import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent
# Data file paths
triangle_data_path = data_dir / 'reported_claims_triangle.csv'
premium_data_path = data_dir / 'earned_premium.csv'
claim_ratio_data_path = data_dir / 'expected_claim_ratio.csv'

# Load the reported claims triangle CSV
df = pd.read_csv(triangle_data_path)
df = df.dropna(how='all')
df = df.set_index('Accident Year')

# Remove commas and convert to numeric values
for col in df.columns:
    df[col] = df[col].astype(str).str.replace(',', '').replace('nan', np.nan)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert the wide format triangle to long format for chainladder
df_long = df.reset_index().melt(
    id_vars=['Accident Year'], 
    var_name='age', 
    value_name='reported'
)
df_long = df_long.dropna()
df_long['age'] = df_long['age'].astype(int)
df_long['Accident Year'] = df_long['Accident Year'].astype(int)

# Create origin period and valuation date for chainladder
df_long['origin_period'] = pd.PeriodIndex(df_long['Accident Year'].astype(str), freq='Y')
df_long['valuation'] = (df_long['origin_period'] + (df_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

# Create the chainladder Triangle
triangle = cl.Triangle(
    df_long, 
    origin='origin_period', 
    development='valuation', 
    columns=['reported'], 
    cumulative=True
)

# Create development pipeline with latest-2 volume weighted averages and 1.05 tail factor
pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=2)),
    ('tail', cl.TailConstant(tail=1.05)),
])
pipe.fit(triangle)

# Load earned premium data
df_premium = pd.read_csv(premium_data_path)
df_premium['earned_premium'] = df_premium['earned_premium'].astype(str).str.replace(',', '').str.replace('"', '')
df_premium['earned_premium'] = pd.to_numeric(df_premium['earned_premium'], errors='coerce')

# Load expected claim ratio data
df_claim_ratio = pd.read_csv(claim_ratio_data_path)
df_claim_ratio['selected_claim_ratio'] = df_claim_ratio['selected_claim_ratio'].astype(str).str.replace('%', '')
df_claim_ratio['selected_claim_ratio'] = pd.to_numeric(df_claim_ratio['selected_claim_ratio'], errors='coerce') / 100

# STEP 1 SOLUTION: Calculate BF Ultimates
df_merged = pd.merge(df_premium, df_claim_ratio, on='accident_year')
df_merged['apriori_ultimate'] = df_merged['earned_premium'] * df_merged['selected_claim_ratio']

# Create apriori triangle with same structure as loss triangle
apriori_array = np.zeros_like(triangle.values)
for i, row in df_merged.iterrows():
    apriori_array[0, 0, i, :] = row['apriori_ultimate']

apriori_triangle = triangle.copy()
apriori_triangle.values = apriori_array

# Apply Bornhuetter-Ferguson method with pipeline
bf_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=2)),
    ('tail', cl.TailConstant(tail=1.05)),
    ('model', cl.BornhuetterFerguson(apriori=1.0))
])

bf_pipe.fit(triangle, sample_weight=apriori_triangle.latest_diagonal)

# BF ultimate from Step 1
bf_ultimate = bf_pipe.named_steps.model.ultimate_
total_bf_ultimate = bf_ultimate.sum().sum()

### STEP 2: Extract BF IBNR
# Access the IBNR from the BF model and calculate total
# Store results in: total_bf_ibnr

