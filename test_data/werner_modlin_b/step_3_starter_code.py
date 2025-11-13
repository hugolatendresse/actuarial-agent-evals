import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'werner_modlin_b'

state_data = pd.read_csv(data_dir / 'state_earned_exposures_and_reported_loss_paid_alae.csv', thousands=',')
regional_qtrly_pp = pd.read_csv(data_dir / 'regional_quarterly_paid_pure_premium_with_alae.csv', thousands=',')
triangle_df = pd.read_csv(data_dir / 'countrywide_reported_loss_paid_alae_triangle.csv', thousands=',')


def load_triangle_from_csv(df):
    df_long = df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
    df_long = df_long.dropna()
    df_long['age'] = df_long['age'].str.extract(r'(\d+)').astype(int)
    
    df_long['origin'] = pd.to_datetime(df_long['Accident Year'].astype(str) + '-01-01')
    df_long['valuation'] = df_long.apply(
        lambda row: row['origin'] + relativedelta(months=int(row['age'])) - pd.Timedelta(days=1), 
        axis=1
    )
    
    tri = cl.Triangle(
        df_long,
        origin='origin',
        development='valuation',
        columns=['value'],
        cumulative=True
    )
    return tri


def exponential_trend_fit(data_series, n_points):
    if len(data_series) < n_points:
        raise ValueError(f"Data series has {len(data_series)} points but {n_points} requested")
    
    if hasattr(data_series, 'values'):
        recent_data = data_series[-n_points:].values
    else:
        recent_data = data_series[-n_points:]
    
    x = np.arange(n_points)
    log_y = np.log(recent_data)
    
    coeffs = np.polyfit(x, log_y, 1)
    slope = coeffs[0]
    
    trend_rate = np.exp(slope) - 1
    
    return trend_rate


countrywide_tri = load_triangle_from_csv(triangle_df)
countrywide_tri = countrywide_tri[countrywide_tri.origin <= '2015']

pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='simple')),
    ('tail', cl.TailConstant(tail=1.01, attachment_age=63)),
    ('model', cl.Chainladder())
])

pipe.fit(countrywide_tri)

dev_obj = pipe.named_steps.dev
model_obj = pipe.named_steps.model

ldf_values = dev_obj.ldf_.values[0, 0, 0, :]
cdf_values_with_tail = model_obj.cdf_.values[0, 0, 0, :]

accident_years = state_data['Calendar / Accident Year'].tolist()
reported_losses = state_data['Non-Cat Reported Losses and Paid ALAE'].tolist()

cdf_indices = [5, 4, 3, 2, 1]

state_ultimate_losses = []
for ay, reported, cdf_idx in zip(accident_years, reported_losses, cdf_indices):
    ultimate = reported * cdf_values_with_tail[cdf_idx]
    state_ultimate_losses.append(ultimate)

pure_premium_series = regional_qtrly_pp['Paid Pure Premium (including ALAE)']

current_trend_quarterly_8pt = exponential_trend_fit(pure_premium_series, n_points=8)
current_loss_trend_annual = (1 + current_trend_quarterly_8pt) ** 4 - 1

projected_trend_quarterly_4pt = exponential_trend_fit(pure_premium_series, n_points=4)
projected_loss_trend_annual = (1 + projected_trend_quarterly_4pt) ** 4 - 1

### STEP 3: Calculate Total Loss Trend Factors (Two-Step)


