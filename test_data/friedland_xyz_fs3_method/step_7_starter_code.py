import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent
reported_count_data_path = data_dir / 'reported_claim_count_triangle.csv'
cwp_count_data_path = data_dir / 'closed_with_pay_claim_count_triangle.csv'
paid_claims_data_path = data_dir / 'cumulative_paid_claims.csv'

reported_count_df = pd.read_csv(reported_count_data_path)
cwp_count_df = pd.read_csv(cwp_count_data_path)
paid_claims_df = pd.read_csv(paid_claims_data_path)

reported_count_df = reported_count_df[reported_count_df['Accident Year'] >= 2001]
cwp_count_df = cwp_count_df[cwp_count_df['Accident Year'] >= 2001]
paid_claims_df = paid_claims_df[paid_claims_df['Accident Year'] >= 2001]

reported_count_long = reported_count_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
reported_count_long = reported_count_long.dropna()
reported_count_long['age'] = reported_count_long['age'].astype(int)
reported_count_long['origin_period'] = pd.PeriodIndex(reported_count_long['Accident Year'].astype(int).astype(str), freq='Y')
reported_count_long['valuation'] = (reported_count_long['origin_period'] + (reported_count_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

cwp_count_long = cwp_count_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
cwp_count_long = cwp_count_long.dropna()
cwp_count_long['age'] = cwp_count_long['age'].astype(int)
cwp_count_long['origin_period'] = pd.PeriodIndex(cwp_count_long['Accident Year'].astype(int).astype(str), freq='Y')
cwp_count_long['valuation'] = (cwp_count_long['origin_period'] + (cwp_count_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

paid_claims_long = paid_claims_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
paid_claims_long = paid_claims_long.dropna()
paid_claims_long['age'] = paid_claims_long['age'].astype(int)
paid_claims_long['origin_period'] = pd.PeriodIndex(paid_claims_long['Accident Year'].astype(int).astype(str), freq='Y')
paid_claims_long['valuation'] = (paid_claims_long['origin_period'] + (paid_claims_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

reported_count_tri = cl.Triangle(
    reported_count_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

cwp_count_tri = cl.Triangle(
    cwp_count_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

paid_claims_tri = cl.Triangle(
    paid_claims_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

reported_count_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

reported_count_pipe.fit(reported_count_tri)
reported_count_ultimate = reported_count_pipe.named_steps.model.ultimate_

disposal_rate_tri = cwp_count_tri / reported_count_ultimate

selected_disposal_rates_output = []
n_periods = 2

for j in range(disposal_rate_tri.shape[3]):
    col_values = disposal_rate_tri.values[0, 0, :, j]
    valid_values = col_values[~np.isnan(col_values)]
    
    if len(valid_values) >= n_periods:
        selected_rate = np.mean(valid_values[-n_periods:])
    elif len(valid_values) > 0:
        selected_rate = np.mean(valid_values)
    else:
        break
    
    selected_disposal_rates_output.append(selected_rate)

selected_disposal_rates_output.append(1.00)

latest_cwp_by_ay = cwp_count_tri.latest_diagonal.values[0, 0, :, 0]
ultimate_reported_by_ay = reported_count_ultimate.values[0, 0, :, -1]
n_origins = len(latest_cwp_by_ay)
n_dev = len(selected_disposal_rates_output)

projected_incremental_cwp = np.zeros((n_origins, n_dev))

cwp_incremental_array = cwp_count_tri.cum_to_incr().values[0, 0, :, :]
cwp_cumulative_array = cwp_count_tri.values[0, 0, :, :]

for i in range(n_origins):
    last_observed_age_idx = 0
    for j in range(cwp_cumulative_array.shape[1]):
        if not np.isnan(cwp_cumulative_array[i, j]):
            last_observed_age_idx = j
    
    unclosed_count = ultimate_reported_by_ay[i] - latest_cwp_by_ay[i]
    base_disposal_rate = selected_disposal_rates_output[last_observed_age_idx]
    base = unclosed_count / (1 - base_disposal_rate)
    
    for j in range(n_dev):
        if j < cwp_incremental_array.shape[1] and not np.isnan(cwp_incremental_array[i, j]):
            projected_incremental_cwp[i, j] = cwp_incremental_array[i, j]
        else:
            if j == 0:
                disposal_rate_diff = selected_disposal_rates_output[j]
            else:
                disposal_rate_diff = selected_disposal_rates_output[j] - selected_disposal_rates_output[j-1]
            
            projected_incremental_cwp[i, j] = base * disposal_rate_diff

### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###


paid_incremental = paid_claims_tri.cum_to_incr()
cwp_incremental_from_cum = cwp_count_tri.cum_to_incr()
incremental_severity_tri = paid_incremental / cwp_incremental_from_cum
severity_array = incremental_severity_tri.values[0, 0, :, :]

### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###


severity_trend = 1.05
base_year = 2008
adjusted_severity = np.copy(severity_array)

for i in range(n_origins):
    ay = 2001 + i
    years_to_trend = base_year - ay
    
    if ay >= 2007:
        tort_reform_factor = 1.0
    elif ay == 2006:
        tort_reform_factor = (1 - 0.33) / (1 - 0.107)
    else:
        tort_reform_factor = 1 - 0.33
    
    for j in range(severity_array.shape[1]):
        if not np.isnan(severity_array[i, j]):
            trended_value = severity_array[i, j] * (severity_trend ** years_to_trend)
            adjusted_severity[i, j] = trended_value * tort_reform_factor

### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###


selected_adjusted_severities = []
for j in range(5):
    valid_values = []
    for i in range(n_origins):
        if not np.isnan(adjusted_severity[i, j]):
            valid_values.append(adjusted_severity[i, j])
    
    if len(valid_values) >= 2:
        selected_severity = np.mean(valid_values[-2:])
    else:
        selected_severity = np.mean(valid_values)
    
    selected_adjusted_severities.append(selected_severity)

### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###

