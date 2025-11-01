import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from ratemaking.trending import future_average_written_date

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'werner_modlin_a'

cy_earned_premium_df = pd.read_csv(data_dir / 'cy_earned_premium.csv', thousands=',')
cy_earned_exposures_df = pd.read_csv(data_dir / 'cy_earned_exposures.csv', thousands=',')
qtrly_written_premium_exposures_df = pd.read_csv(data_dir / 'qtrly_written_premium_exposures.csv', thousands=',')


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

### STEP 3: Calculate Total Premium Trend Factors (Two-Step Trending)

