import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

script_dir = Path(__file__).resolve().parent
if "ide_results" in str(script_dir):
    project_root = script_dir.parent.parent.parent
    data_dir = project_root / "test_data" / "werner_modlin_b"
else:
    data_dir = script_dir.parent.parent.parent / 'test_data' / 'werner_modlin_b'

state_data = pd.read_csv(data_dir / 'state_earned_exposures_and_reported_loss_paid_alae.csv', thousands=',')
regional_qtrly_pp = pd.read_csv(data_dir / 'regional_quarterly_paid_pure_premium_with_alae.csv', thousands=',')
triangle_df = pd.read_csv(data_dir / 'countrywide_reported_loss_paid_alae_triangle.csv', thousands=',')

effective_date = '1/1/17'
policy_term_months = 12
rates_in_effect_months = 12
total_reported_claim_counts_5yr = 683
claims_for_full_credibility = 1082
regional_non_cat_pure_premium = 585.75
ulae_factor = 1.011812
variable_expense_provision = 0.138
profit_and_contingency_provision = 0.05


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


def calculate_trend_period_years(from_date, to_date):
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    if isinstance(to_date, datetime):
        to_date = to_date.date()
    delta_days = (to_date - from_date).days
    return delta_days / 365.25


def future_average_accident_date(effective_date, rates_in_effect_months, policy_term_months):
    eff_date = datetime.strptime(effective_date, '%m/%d/%y').date()
    months_to_add = (rates_in_effect_months + policy_term_months) // 2
    return eff_date + relativedelta(months=months_to_add)


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

latest_ay = 2015
current_ay_date = datetime(latest_ay, 7, 1).date()

future_avg_accident = future_average_accident_date(effective_date, rates_in_effect_months, policy_term_months)
projected_loss_trend_period = calculate_trend_period_years(current_ay_date, future_avg_accident)

loss_trend_factors = []
for ay in accident_years:
    ay_midpoint = datetime(ay, 7, 1).date()
    current_period = calculate_trend_period_years(ay_midpoint, current_ay_date)
    
    current_loss_trend_factor = (1 + current_loss_trend_annual) ** current_period
    projected_loss_trend_factor = (1 + projected_loss_trend_annual) ** projected_loss_trend_period
    
    total_loss_trend_factor = current_loss_trend_factor * projected_loss_trend_factor
    loss_trend_factors.append(total_loss_trend_factor)

total_loss_trend_factors = np.array(loss_trend_factors)

trended_ultimate_losses = state_ultimate_losses * total_loss_trend_factors
trended_ultimate_losses_with_ulae = trended_ultimate_losses * ulae_factor

total_trended_ultimate_losses = trended_ultimate_losses_with_ulae.sum()
total_earned_exposures = state_data['Earned Exposures'].sum()

selected_projected_non_cat_pure_premium = total_trended_ultimate_losses / total_earned_exposures

z = np.sqrt(total_reported_claim_counts_5yr / claims_for_full_credibility)
z = min(z, 1.0)

credibility_weighted_non_cat_pure_premium = (
    z * selected_projected_non_cat_pure_premium + 
    (1 - z) * regional_non_cat_pure_premium
)

### STEP 6: Calculate Variable Permissible Loss Ratio (VPLR)


