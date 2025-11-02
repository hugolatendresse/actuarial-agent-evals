import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

data_dir = Path(__file__).resolve().parent

state_earned_exp_data_path = data_dir / 'state_earned_exposures_and_reported_loss_paid_alae.csv'
regional_qtrly_pp_data_path = data_dir / 'regional_quarterly_paid_pure_premium_with_alae.csv'
countrywide_triangle_data_path = data_dir / 'countrywide_reported_loss_paid_alae_triangle.csv'

effective_date = '1/1/17'
policy_term_months = 12
rates_in_effect_months = 12
total_reported_claim_counts_5yr = 683
claims_for_full_credibility = 1082
regional_non_cat_pure_premium = 585.75
total_cat_pure_premium = 103.85
ulae_factor = 1.011812
projected_net_reinsurance_cost_per_exposure = 15.68
projected_fixed_expense_per_exposure = 77.74
variable_expense_provision = 0.138
profit_and_contingency_provision = 0.05

print("=" * 80)
print("Werner-Modlin Loss Cost Ratemaking Analysis - Method B")
print("=" * 80)
print(f"\nAssumptions:")
print(f"  Effective date: {effective_date}")
print(f"  Policy term: {policy_term_months} months")
print(f"  Rates in effect: {rates_in_effect_months} months")
print(f"  5-year total reported claims: {total_reported_claim_counts_5yr}")
print(f"  Claims for full credibility: {claims_for_full_credibility}")
print(f"  Regional non-CAT pure premium: ${regional_non_cat_pure_premium:.2f}")
print(f"  Total CAT pure premium: ${total_cat_pure_premium:.2f}")
print(f"  Projected net reinsurance cost per exposure: ${projected_net_reinsurance_cost_per_exposure:.2f}")
print(f"  Projected fixed expense per exposure: ${projected_fixed_expense_per_exposure:.2f}")
print(f"  Variable expense provision: {variable_expense_provision*100:.1f}%")
print(f"  Profit and contingency provision: {profit_and_contingency_provision*100:.0f}%")

print("\n" + "=" * 80)
print("STEP 1: Develop State Losses to Ultimate using Countrywide LDFs")
print("=" * 80)

state_data = pd.read_csv(state_earned_exp_data_path, thousands=',')
regional_qtrly_pp = pd.read_csv(regional_qtrly_pp_data_path, thousands=',')
triangle_df = pd.read_csv(countrywide_triangle_data_path, thousands=',')

print(f"\nLoaded state data for years: {state_data['Calendar / Accident Year'].tolist()}")
print(f"State reported losses: {state_data['Non-Cat Reported Losses and Paid ALAE'].tolist()}")

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

countrywide_tri = load_triangle_from_csv(triangle_df)
countrywide_tri = countrywide_tri[countrywide_tri.origin <= '2015']

print(f"\nCountrywide triangle shape: {countrywide_tri.shape}")
print(f"Countrywide triangle origins: {[int(str(o).split('-')[0]) for o in countrywide_tri.origin]}")
print(f"Countrywide triangle development periods (months): {countrywide_tri.development}")

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

print(f"\nCountrywide LDFs: {ldf_values}")
print(f"Countrywide CDFs (with 1% tail at age 63): {cdf_values_with_tail}")

accident_years = state_data['Calendar / Accident Year'].tolist()
reported_losses = state_data['Non-Cat Reported Losses and Paid ALAE'].tolist()

cdf_indices = [5, 4, 3, 2, 1]

state_ultimate_losses = []
print(f"\nState Ultimate Losses by Accident Year:")
for ay, reported, cdf_idx in zip(accident_years, reported_losses, cdf_indices):
    ultimate = reported * cdf_values_with_tail[cdf_idx]
    state_ultimate_losses.append(ultimate)
    print(f"  AY {ay}: ${ultimate:,.2f}")

print(f"\nTotal ultimate losses: ${sum(state_ultimate_losses):,.2f}")

print("\n" + "=" * 80)
print("STEP 2: Calculate Loss Trends from Regional Pure Premium Data")
print("=" * 80)

def exponential_trend_fit(data_series, n_points):
    """
    Fit exponential trend using least squares (Excel LOGEST method).
    """
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

pure_premium_series = regional_qtrly_pp['Paid Pure Premium (including ALAE)']

current_trend_quarterly_8pt = exponential_trend_fit(pure_premium_series, n_points=8)
current_loss_trend_annual = (1 + current_trend_quarterly_8pt) ** 4 - 1

projected_trend_quarterly_4pt = exponential_trend_fit(pure_premium_series, n_points=4)
projected_loss_trend_annual = (1 + projected_trend_quarterly_4pt) ** 4 - 1

print(f"\nCurrent loss trend (8-point): {current_loss_trend_annual:.6f} ({current_loss_trend_annual*100:.5f}%)")
print(f"Projected loss trend (4-point): {projected_loss_trend_annual:.6f} ({projected_loss_trend_annual*100:.5f}%)")

print("\n" + "=" * 80)
print("STEP 3: Calculate Total Loss Trend Factors (Two-Step)")
print("=" * 80)

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

print(f"\nLatest Accident Year: {latest_ay}")
print(f"Current AY Date (midpoint): {current_ay_date}")
print(f"Future Average Accident Date: {future_avg_accident}")
print(f"Projected Loss Trend Period: {projected_loss_trend_period:.4f} years")

print("\nTotal Loss Trend Factors by Accident Year:")
for ay, factor in zip(accident_years, total_loss_trend_factors):
    print(f"  AY {ay}: {factor:.4f}")

print("\n" + "=" * 80)
print("STEP 4: Calculate Selected Projected Non-CAT Pure Premium")
print("=" * 80)

trended_ultimate_losses = state_ultimate_losses * total_loss_trend_factors
trended_ultimate_losses_with_ulae = trended_ultimate_losses * ulae_factor

total_trended_ultimate_losses = trended_ultimate_losses_with_ulae.sum()
total_earned_exposures = state_data['Earned Exposures'].sum()

selected_projected_non_cat_pure_premium = total_trended_ultimate_losses / total_earned_exposures

print(f"\nULAE Factor: {ulae_factor:.6f}")
print(f"Total Trended Ultimate Losses (with ULAE): ${total_trended_ultimate_losses:,.2f}")
print(f"Total Earned Exposures: {total_earned_exposures:,.0f}")
print(f"Selected Projected Non-CAT Pure Premium: ${selected_projected_non_cat_pure_premium:.5f}")

print("\n" + "=" * 80)
print("STEP 5: Calculate Credibility-Weighted Non-CAT Pure Premium")
print("=" * 80)

z = np.sqrt(total_reported_claim_counts_5yr / claims_for_full_credibility)
z = min(z, 1.0)

credibility_weighted_non_cat_pure_premium = (
    z * selected_projected_non_cat_pure_premium + 
    (1 - z) * regional_non_cat_pure_premium
)

print(f"\nTotal Claims (5-year): {total_reported_claim_counts_5yr}")
print(f"Claims for Full Credibility: {claims_for_full_credibility}")
print(f"Credibility Factor (Z): {z:.6f} ({z*100:.3f}%)")
print(f"Selected Projected Non-CAT Pure Premium: ${selected_projected_non_cat_pure_premium:.5f}")
print(f"Regional Non-CAT Pure Premium (complement): ${regional_non_cat_pure_premium:.2f}")
print(f"Credibility-Weighted Non-CAT Pure Premium: ${credibility_weighted_non_cat_pure_premium:.4f}")

print("\n" + "=" * 80)
print("STEP 6: Calculate Variable Permissible Loss Ratio (VPLR)")
print("=" * 80)

vplr = 1 - variable_expense_provision - profit_and_contingency_provision

print(f"\nVariable Expense Provision: {variable_expense_provision:.3f} ({variable_expense_provision*100:.1f}%)")
print(f"Profit and Contingency Provision: {profit_and_contingency_provision:.3f} ({profit_and_contingency_provision*100:.1f}%)")
print(f"VPLR: {vplr:.3f} ({vplr*100:.1f}%)")

print("\n" + "=" * 80)
print("STEP 7: Calculate Total Indicated Pure Premium")
print("=" * 80)

total_indicated_pure_premium = (
    credibility_weighted_non_cat_pure_premium + 
    total_cat_pure_premium + 
    projected_net_reinsurance_cost_per_exposure + 
    projected_fixed_expense_per_exposure
) / vplr

print(f"\nCredibility-Weighted Non-CAT Pure Premium: ${credibility_weighted_non_cat_pure_premium:.2f}")
print(f"Total CAT Pure Premium: ${total_cat_pure_premium:.2f}")
print(f"Projected Net Reinsurance Cost per Exposure: ${projected_net_reinsurance_cost_per_exposure:.2f}")
print(f"Projected Fixed Expense per Exposure: ${projected_fixed_expense_per_exposure:.2f}")
print(f"Sum of Components: ${credibility_weighted_non_cat_pure_premium + total_cat_pure_premium + projected_net_reinsurance_cost_per_exposure + projected_fixed_expense_per_exposure:.2f}")
print(f"\nVPLR: {vplr:.3f} ({vplr*100:.1f}%)")
print(f"\nTotal Indicated Pure Premium: ${total_indicated_pure_premium:.2f}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

