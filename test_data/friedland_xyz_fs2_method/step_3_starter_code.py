import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'friedland_xyz_fs2_method'
reported_count_data_path = data_dir / 'reported_claim_count_triangle.csv'
premium_data_path = data_dir / 'earned_premium_and_rate_changes.csv'

reported_count_df = pd.read_csv(reported_count_data_path, thousands=',')

reported_count_long = reported_count_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
reported_count_long = reported_count_long.dropna()
reported_count_long['age'] = reported_count_long['age'].astype(int)
reported_count_long['origin_period'] = pd.PeriodIndex(reported_count_long['Accident Year'].astype(int).astype(str), freq='Y')
reported_count_long['valuation'] = (reported_count_long['origin_period'] + (reported_count_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

reported_count_tri = cl.Triangle(
    reported_count_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

count_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

count_pipe.fit(reported_count_tri)
count_ultimate = count_pipe.named_steps.model.ultimate_
count_total_ultimate = count_ultimate.sum().sum()
count_ultimates_by_ay = count_ultimate.values[0, 0, :, -1]

years = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
claim_count_trend = -0.015

trended_count_dict = {}
for year in range(2002, 2007):
    ay_idx = years.index(year)
    years_to_trend = 2008 - year
    trend_factor = (1 + claim_count_trend) ** years_to_trend
    trended_count = count_ultimates_by_ay[ay_idx] * trend_factor
    trended_count_dict[year] = trended_count

### STEP 3: Calculate On-Level Earned Premiums

