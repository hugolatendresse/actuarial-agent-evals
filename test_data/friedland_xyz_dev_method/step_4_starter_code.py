import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

# Data file paths
data_path_1 = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_dev_method/current_level_earned_premium.csv'
data_path_2 = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_dev_method/reported_claims_triangle.csv'

### STEP 1: Load Triangle Data (from reference implementation)
# Load and clean the CSV data  
df = pd.read_csv(data_path_2, thousands=',')
df_clean = df.copy()
df_clean = df_clean.rename(columns={'Accident Year': 'AccidentYear'})

value_columns = [col for col in df_clean.columns if col != 'AccidentYear']
for col in value_columns:
    df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(',', ''), errors='coerce')

df_clean = df_clean[df_clean['AccidentYear'].notna()]
df_clean['AccidentYear'] = df_clean['AccidentYear'].astype(int)
df_clean = df_clean.dropna(how='all', subset=value_columns)

# Convert to long format with proper dates
df_melted = df_clean.melt(id_vars=['AccidentYear'], var_name='development', value_name='values')
df_melted = df_melted.dropna(subset=['values'])
df_melted['development'] = df_melted['development'].astype(int)

df_melted['origin'] = pd.to_datetime(df_melted['AccidentYear'], format='%Y')
df_melted['valuation'] = df_melted.apply(
    lambda row: row['origin'] + pd.DateOffset(months=int(row['development'])-1), 
    axis=1
)

# Create chainladder Triangle
triangle = cl.Triangle(
    df_melted,
    origin='origin',
    development='valuation',
    columns='values',
    cumulative=True
)

### STEP 2: Calculate Volume-Weighted Average LDFs (from reference implementation)
dev_weighted = cl.Development(average='volume', n_periods=3)
dev_weighted.fit(triangle)
ldfs_weighted = dev_weighted.ldf_.values[0, 0, 0, :]


### STEP 3: Calculate Simple Average LDFs (from reference implementation)
dev_simple = cl.Development(average='simple', n_periods=5)
dev_simple.fit(triangle)
ldfs_simple = dev_simple.ldf_.values[0, 0, 0, :]


### STEP 4: Calculate CDFs with Tail Factor
# Write your code below to apply tail factor (1.00) using chainladder.TailConstant
