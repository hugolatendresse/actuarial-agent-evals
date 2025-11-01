import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from ratemaking.trending import future_average_written_date, future_average_accident_date
import chainladder as cl

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'werner_modlin_a'

cy_earned_premium_df = pd.read_csv(data_dir / 'cy_earned_premium.csv', thousands=',')
cy_earned_exposures_df = pd.read_csv(data_dir / 'cy_earned_exposures.csv', thousands=',')
qtrly_written_premium_exposures_df = pd.read_csv(data_dir / 'qtrly_written_premium_exposures.csv', thousands=',')
qtrly_regional_loss_trend_df = pd.read_csv(data_dir / 'qtrly_regional_loss_trend_data.csv', thousands=',')
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

reported_loss_long = reported_loss_alae_triangle_df.melt(
    id_vars=['Accident Year'], 
    var_name='age', 
    value_name='value'
)
reported_loss_long = reported_loss_long.dropna()
reported_loss_long['age'] = reported_loss_long['age'].str.extract('(\d+)').astype(int)
reported_loss_long['origin_period'] = pd.PeriodIndex(
    reported_loss_long['Accident Year'].astype(int).astype(str), 
    freq='Y'
)
reported_loss_long['valuation'] = (
    reported_loss_long['origin_period'] + 
    (reported_loss_long['age'].astype(int) // 12) - 1
).dt.to_timestamp(how='end')

loss_tri = cl.Triangle(
    reported_loss_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

loss_dev = cl.Development(average='simple', drop_high=True, drop_low=True)
loss_dev.fit(loss_tri)

loss_tail = cl.TailConstant(tail=1.0)
loss_tail.fit(loss_dev.transform(loss_tri))

loss_model = cl.Chainladder()
loss_model.fit(loss_tail.transform(loss_dev.transform(loss_tri)))

loss_ultimate = loss_model.ultimate_
step_5_ultimate_losses = loss_ultimate.values[0, 0, :, -1]

qtrly_regional_loss_trend_df['Frequency'] = (
    qtrly_regional_loss_trend_df['Closed Claim Count'] / 
    qtrly_regional_loss_trend_df['Earned Exposure']
)

qtrly_regional_loss_trend_df['Severity'] = (
    qtrly_regional_loss_trend_df['Paid Losses'] / 
    qtrly_regional_loss_trend_df['Closed Claim Count']
)

frequency_series = qtrly_regional_loss_trend_df['Frequency']
severity_series = qtrly_regional_loss_trend_df['Severity']

frequency_trend_8pt = exponential_trend_fit(frequency_series, n_points=8)
severity_trend_8pt = exponential_trend_fit(severity_series, n_points=8)

frequency_annual_8pt = (1 + frequency_trend_8pt) ** 4 - 1
severity_annual_8pt = (1 + severity_trend_8pt) ** 4 - 1

step_6_current_loss_trend = (1 + frequency_annual_8pt) * (1 + severity_annual_8pt) - 1

frequency_trend_4pt = exponential_trend_fit(frequency_series, n_points=4)
severity_trend_4pt = exponential_trend_fit(severity_series, n_points=4)

frequency_annual_4pt = (1 + frequency_trend_4pt) ** 4 - 1
severity_annual_4pt = (1 + severity_trend_4pt) ** 4 - 1

step_7_projected_loss_trend = (1 + frequency_annual_4pt) * (1 + severity_annual_4pt) - 1

accident_years = cy_earned_premium_df['Calendar Year'].values
latest_ay = accident_years[-1]
current_ay_date = datetime(latest_ay, 7, 1).date()

future_avg_accident = future_average_accident_date(effective_date, rates_in_effect_months, policy_term_months)
projected_loss_trend_period = calculate_trend_period_years(current_ay_date, future_avg_accident)

loss_trend_factors = []
for ay in accident_years:
    ay_midpoint = datetime(ay, 7, 1).date()
    current_period = calculate_trend_period_years(ay_midpoint, current_ay_date)
    
    current_loss_trend_factor = (1 + step_6_current_loss_trend) ** current_period
    projected_loss_trend_factor = (1 + step_7_projected_loss_trend) ** projected_loss_trend_period
    
    total_loss_trend_factor = current_loss_trend_factor * projected_loss_trend_factor
    loss_trend_factors.append(total_loss_trend_factor)

step_8_total_loss_trend_factors = np.array(loss_trend_factors)

ulae_factor = 1.143

ay_start_idx = list(reported_loss_alae_triangle_df['Accident Year']).index(2011)
ultimate_losses_2011_2015 = step_5_ultimate_losses[ay_start_idx:]
projected_ultimate_losses = ultimate_losses_2011_2015 * step_8_total_loss_trend_factors

total_projected_ultimate_losses = projected_ultimate_losses.sum()
total_projected_earned_premium = step_4_projected_earned_premium.sum()

step_9_projected_loss_lae_ratio = (total_projected_ultimate_losses / total_projected_earned_premium) * ulae_factor

variable_expense_provision = 0.169956
underwriting_profit_provision = 0.05

step_10_vplr = 1 - variable_expense_provision - underwriting_profit_provision

fixed_expense_provision = 0.112867

step_11_indicated_rate_change = ((step_9_projected_loss_lae_ratio + fixed_expense_provision) / step_10_vplr) - 1

total_claims = 700
claims_for_full_credibility = 1082

step_12_credibility = np.sqrt(total_claims / claims_for_full_credibility)

latest_indicated_rate_change = 0.132
last_rate_change_eff_date = '1/1/2016'
last_rate_change_taken = 0.05

net_trend = (1 + step_7_projected_loss_trend) / (1 + step_2_premium_trend) - 1

trend_from_date = datetime(2016, 1, 1).date()
trend_to_date = datetime(2017, 1, 1).date()
trend_period_years = calculate_trend_period_years(trend_from_date, trend_to_date)

step_13_trended_present_rates = (1 + net_trend) ** trend_period_years * ((1 + latest_indicated_rate_change) / (1 + last_rate_change_taken)) - 1

### STEP 14: Calculate Credibility-Weighted Rate Change

