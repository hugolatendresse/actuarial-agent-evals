import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from ratemaking.trending import future_average_written_date
import chainladder as cl

script_dir = Path(__file__).resolve().parent
if "ide_results" in str(script_dir):
    project_root = script_dir.parent.parent.parent
    data_dir = project_root / "test_data" / "werner_modlin_a"
else:
    data_dir = script_dir.parent.parent.parent / 'test_data' / 'werner_modlin_a'

cy_earned_premium_df = pd.read_csv(data_dir / 'cy_earned_premium.csv', thousands=',')
cy_earned_exposures_df = pd.read_csv(data_dir / 'cy_earned_exposures.csv', thousands=',')
qtrly_written_premium_exposures_df = pd.read_csv(data_dir / 'qtrly_written_premium_exposures.csv', thousands=',')
reported_loss_alae_triangle_df = pd.read_csv(data_dir / 'reported_loss_alae_triangle.csv', thousands=',')


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


def calculate_trend_period_years(from_date, to_date):
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    if isinstance(to_date, datetime):
        to_date = to_date.date()
    
    delta_days = (to_date - from_date).days
    return delta_days / 365.25


cy_earned_premium_df['Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium'] * 
    cy_earned_premium_df['Current Rate Level Factor']
)

step_1_earned_premium_crl = cy_earned_premium_df['Earned Premium at CRL'].values

qtrly_df = qtrly_written_premium_exposures_df.copy()
qtrly_df['Average Written Premium at CRL'] = (
    qtrly_df['Written Premium at CRL'] / 
    qtrly_df['Written Exposure']
)

rolling_annual_premium = []
rolling_annual_exposure = []

for i in range(3, len(qtrly_df)):
    annual_premium = qtrly_df['Written Premium at CRL'].iloc[i-3:i+1].sum()
    annual_exposure = qtrly_df['Written Exposure'].iloc[i-3:i+1].sum()
    rolling_annual_premium.append(annual_premium)
    rolling_annual_exposure.append(annual_exposure)

rolling_avg_premium = np.array(rolling_annual_premium) / np.array(rolling_annual_exposure)

quarterly_trend = exponential_trend_fit(rolling_avg_premium, n_points=8)

step_2_premium_trend = (1 + quarterly_trend) ** 4 - 1

avg_written_premium_series = qtrly_df['Average Written Premium at CRL']

policy_term_months = 6
rates_in_effect_months = 12
effective_date = '1/1/2017'
latest_cy = 2015
current_date = datetime(latest_cy, 7, 1).date()

future_avg_written = future_average_written_date(effective_date, rates_in_effect_months)
projected_trend_period = calculate_trend_period_years(current_date, future_avg_written)

cy_earned_premium_df['Average Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium at CRL'] / 
    cy_earned_exposures_df['Earned Exposure']
)

latest_avg_written_premium_crl = avg_written_premium_series.iloc[-1]

cy_earned_premium_df['Current Trend Factor'] = (
    latest_avg_written_premium_crl / 
    cy_earned_premium_df['Average Earned Premium at CRL']
)

projected_trend_factor = (1 + step_2_premium_trend) ** projected_trend_period

cy_earned_premium_df['Total Trend Factor'] = (
    cy_earned_premium_df['Current Trend Factor'] * projected_trend_factor
)

step_3_total_trend_factors = cy_earned_premium_df['Total Trend Factor'].values

cy_earned_premium_df['Projected Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium at CRL'] * 
    cy_earned_premium_df['Total Trend Factor']
)

step_4_projected_earned_premium = cy_earned_premium_df['Projected Earned Premium at CRL'].values

### STEP 5: Develop Losses to Ultimate

