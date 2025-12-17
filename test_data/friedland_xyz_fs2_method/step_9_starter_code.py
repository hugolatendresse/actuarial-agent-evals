import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

script_dir = Path(__file__).resolve().parent
if "ide_results" in str(script_dir):
    project_root = script_dir.parent.parent.parent
    data_dir = project_root / "test_data" / "friedland_xyz_fs2_method"
else:
    data_dir = script_dir.parent.parent.parent / 'test_data' / 'friedland_xyz_fs2_method'
reported_count_data_path = data_dir / 'reported_claim_count_triangle.csv'
reported_claims_data_path = data_dir / 'reported_claims_triangle.csv'
premium_data_path = data_dir / 'earned_premium_and_rate_changes.csv'

reported_count_df = pd.read_csv(reported_count_data_path, thousands=',')
reported_claims_df = pd.read_csv(reported_claims_data_path, thousands=',')

reported_count_long = reported_count_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
reported_count_long = reported_count_long.dropna()
reported_count_long['age'] = reported_count_long['age'].astype(int)
reported_count_long['origin_period'] = pd.PeriodIndex(reported_count_long['Accident Year'].astype(int).astype(str), freq='Y')
reported_count_long['valuation'] = (reported_count_long['origin_period'] + (reported_count_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

reported_claims_long = reported_claims_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
reported_claims_long = reported_claims_long.dropna()
reported_claims_long['age'] = reported_claims_long['age'].astype(int)
reported_claims_long['origin_period'] = pd.PeriodIndex(reported_claims_long['Accident Year'].astype(int).astype(str), freq='Y')
reported_claims_long['valuation'] = (reported_claims_long['origin_period'] + (reported_claims_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

reported_count_tri = cl.Triangle(
    reported_count_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

reported_claims_tri = cl.Triangle(
    reported_claims_long,
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

premium_df = pd.read_csv(premium_data_path, thousands=',')
premium_df['Rate Changes'] = premium_df['Rate Changes'].fillna('0%')
premium_df['rate_change_pct'] = premium_df['Rate Changes'].str.rstrip('%').astype(float) / 100
premium_df['rate_factor'] = 1 + premium_df['rate_change_pct']
premium_df['cumulative_rate_factor'] = premium_df['rate_factor'].cumprod()

target_cumulative = premium_df.loc[premium_df['Accident Year'] == 2008, 'cumulative_rate_factor'].values[0]
premium_df['onlevel_factor'] = target_cumulative / premium_df['cumulative_rate_factor']
premium_df['onlevel_premium'] = premium_df['Earned Premium'] * premium_df['onlevel_factor']

onlevel_premiums = premium_df['onlevel_premium'].tolist()

trended_freq_to_olep = {}
for year in range(2002, 2007):
    trended_count = trended_count_dict[year]
    olep = premium_df.loc[premium_df['Accident Year'] == year, 'onlevel_premium'].values[0]
    freq = trended_count / (olep / 1000)
    trended_freq_to_olep[year] = freq

selected_2008_freq = np.mean([trended_freq_to_olep[2005], trended_freq_to_olep[2006]])

unadjusted_freqs = []
for i, year in enumerate(years):
    rate_olf = premium_df.loc[premium_df['Accident Year'] == year, 'onlevel_factor'].values[0]
    years_from_2008 = 2008 - year
    count_trend_factor = (1 + claim_count_trend) ** years_from_2008
    
    unadj_freq = (selected_2008_freq * rate_olf) / count_trend_factor
    unadjusted_freqs.append(unadj_freq)

projected_counts = []
for i, year in enumerate(years):
    ep = premium_df.loc[premium_df['Accident Year'] == year, 'Earned Premium'].values[0]
    proj_count = unadjusted_freqs[i] * (ep / 1000)
    projected_counts.append(proj_count)

severity_tri = reported_claims_tri / reported_count_tri

severity_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='simple', n_periods=5)),
    ('tail', cl.TailConstant(tail=1.01)),
    ('model', cl.Chainladder())
])

severity_pipe.fit(severity_tri)
severity_ultimate = severity_pipe.named_steps.model.ultimate_
severity_ultimates_by_ay = severity_ultimate.values[0, 0, :, -1]

severity_trend = 0.05

### STEP 9: Adjust Severities to 2008 Level (AY 1998-2006)

