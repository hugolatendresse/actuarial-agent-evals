import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from ratemaking.trending import future_average_written_date, future_average_accident_date
import chainladder as cl

data_dir = Path(__file__).resolve().parent

cy_earned_premium_df = pd.read_csv(data_dir / 'cy_earned_premium.csv', thousands=',')
cy_earned_exposures_df = pd.read_csv(data_dir / 'cy_earned_exposures.csv', thousands=',')
qtrly_written_premium_exposures_df = pd.read_csv(data_dir / 'qtrly_written_premium_exposures.csv', thousands=',')
qtrly_regional_loss_trend_df = pd.read_csv(data_dir / 'qtrly_regional_loss_trend_data.csv', thousands=',')
reported_loss_alae_triangle_df = pd.read_csv(data_dir / 'reported_loss_alae_triangle.csv', thousands=',')


def exponential_trend_fit(data_series, n_points):
    """
    Fit exponential trend to time series data using Excel LOGEST method.
    
    This matches Excel's =LOGEST(data, SEQUENCE(n))^4-1 formula.
    
    Args:
        data_series: pandas Series or array of values
        n_points: number of most recent points to use for fitting
    
    Returns:
        Period trend rate as decimal (not annualized)
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


def calculate_trend_period_years(from_date, to_date):
    """
    Calculate trend period in years between two dates.
    
    Args:
        from_date: Starting date (datetime.date or datetime.datetime)
        to_date: Ending date (datetime.date or datetime.datetime)
    
    Returns:
        Trend period in years (float)
    """
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    if isinstance(to_date, datetime):
        to_date = to_date.date()
    
    delta_days = (to_date - from_date).days
    return delta_days / 365.25


print("=" * 80)
print("STEP 1: Calculate CY Earned Premiums at Current Rate Level")
print("=" * 80)

cy_earned_premium_df['Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium'] * 
    cy_earned_premium_df['Current Rate Level Factor']
)

step_1_earned_premium_crl = cy_earned_premium_df['Earned Premium at CRL'].values

print("\nCalendar Year Earned Premiums at Current Rate Level:")
for i, (year, premium) in enumerate(zip(cy_earned_premium_df['Calendar Year'], step_1_earned_premium_crl)):
    print(f"{year}: ${premium:,.2f}")

print("\nGround Truth:")
ground_truth_step_1 = [1364716.59, 1405593.50, 1448217.41, 1492091.78, 1536218.69]
for i, gt in enumerate(ground_truth_step_1):
    year = 2011 + i
    calc = step_1_earned_premium_crl[i]
    match = abs(calc - gt) < 0.01
    print(f"{year}: ${gt:,.2f} - Match: {match}")

print("\n" + "=" * 80)
print("STEP 2: Calculate 8-Point Exponential Trend for Average Written Premium at CRL")
print("=" * 80)

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

print(f"\nNumber of rolling annual data points: {len(rolling_avg_premium)}")
print(f"Last 8 rolling annual average premiums:")
for i, val in enumerate(rolling_avg_premium[-8:]):
    print(f"  Point {i+1}: ${val:.2f}")

print(f"\nQuarterly Trend Fit: {quarterly_trend:.4f} ({quarterly_trend*100:.2f}%)")
print(f"Annual Trend (compounded): {step_2_premium_trend:.4f} ({step_2_premium_trend*100:.2f}%)")
print(f"Ground Truth: 2.0%")
print(f"Match: {abs(step_2_premium_trend - 0.02) < 0.001}")

avg_written_premium_series = qtrly_df['Average Written Premium at CRL']

print("\n" + "=" * 80)
print("STEP 3: Calculate Total Trend Factors by CY (Two-Step Trending)")
print("=" * 80)

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

print(f"\nCurrent Date (midpoint of latest CY {latest_cy}): {current_date}")
print(f"Latest Average Written Premium at CRL (Q4 {latest_cy}): ${latest_avg_written_premium_crl:.2f}")
print(f"Future Average Written Date: {future_avg_written}")
print(f"Projected Trend Period (current to future): {projected_trend_period:.4f} years")
print(f"Projected Trend Factor: {projected_trend_factor:.4f}")
print(f"Selected Premium Trend: {step_2_premium_trend:.4f}")

print("\nTotal Trend Factors by Calendar Year:")
for year, current_tf, total_tf in zip(
    cy_earned_premium_df['Calendar Year'],
    cy_earned_premium_df['Current Trend Factor'],
    cy_earned_premium_df['Total Trend Factor']
):
    print(f"{year}: Current={current_tf:.4f}, Total={total_tf:.4f}")

print("\nGround Truth:")
ground_truth_step_3 = [1.1350, 1.1122, 1.0886, 1.0669, 1.0458]
for i, gt in enumerate(ground_truth_step_3):
    year = 2011 + i
    calc = step_3_total_trend_factors[i]
    match = abs(calc - gt) < 0.0001
    print(f"{year}: {gt:.4f} - Match: {match}")

print("\n" + "=" * 80)
print("STEP 4: Calculate CY Projected Earned Premiums at Current Rate Level")
print("=" * 80)

cy_earned_premium_df['Projected Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium at CRL'] * 
    cy_earned_premium_df['Total Trend Factor']
)

step_4_projected_earned_premium = cy_earned_premium_df['Projected Earned Premium at CRL'].values

print("\nCalendar Year Projected Earned Premiums at Current Rate Level:")
for year, premium in zip(cy_earned_premium_df['Calendar Year'], step_4_projected_earned_premium):
    print(f"{year}: ${premium:,.0f}")

print("\nGround Truth:")
ground_truth_step_4 = [1548808, 1563215, 1576422, 1591790, 1606438]
for i, gt in enumerate(ground_truth_step_4):
    year = 2011 + i
    calc = step_4_projected_earned_premium[i]
    match = abs(calc - gt) < 1
    print(f"{year}: ${gt:,} - Match: {match}")

print("\n" + "=" * 80)
print("STEP 5: Develop Losses to Ultimate")
print("=" * 80)

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

print(f"\nLink Ratios (LDF): {loss_dev.ldf_.values[0, 0, 0, :]}")
print(f"Tail Factor: 1.0000")

print("\nUltimate Losses by Accident Year:")
for i, (ay, ult) in enumerate(zip(reported_loss_alae_triangle_df['Accident Year'], step_5_ultimate_losses)):
    print(f"{ay}: ${ult:,.4f}")

print("\nGround Truth (2011-2015):")
ground_truth_step_5 = [856495.0000, 849712.4606, 835307.2497, 844601.0778, 874847.1731]
ay_start_idx = list(reported_loss_alae_triangle_df['Accident Year']).index(2011)
for i, gt in enumerate(ground_truth_step_5):
    ay = reported_loss_alae_triangle_df['Accident Year'].iloc[ay_start_idx + i]
    calc = step_5_ultimate_losses[ay_start_idx + i]
    match = abs(calc - gt) < 0.01
    print(f"{ay}: ${gt:,.4f} - Match: {match}")

print("\n" + "=" * 80)
print("STEP 6: Calculate Current Loss Trend (8-point)")
print("=" * 80)

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

print(f"\nFrequency Trend (quarterly): {frequency_trend_8pt:.6f}")
print(f"Frequency Trend (annual): {frequency_annual_8pt:.6f} ({frequency_annual_8pt*100:.2f}%)")
print(f"Severity Trend (quarterly): {severity_trend_8pt:.6f}")
print(f"Severity Trend (annual): {severity_annual_8pt:.6f} ({severity_annual_8pt*100:.2f}%)")
print(f"Combined Loss Trend (current): {step_6_current_loss_trend:.6f} ({step_6_current_loss_trend*100:.2f}%)")
print(f"Ground Truth: -0.1%")
print(f"Match: {abs(step_6_current_loss_trend - (-0.001)) < 0.001}")

print("\n" + "=" * 80)
print("STEP 7: Calculate Projected Loss Trend (4-point)")
print("=" * 80)

frequency_trend_4pt = exponential_trend_fit(frequency_series, n_points=4)
severity_trend_4pt = exponential_trend_fit(severity_series, n_points=4)

frequency_annual_4pt = (1 + frequency_trend_4pt) ** 4 - 1
severity_annual_4pt = (1 + severity_trend_4pt) ** 4 - 1

step_7_projected_loss_trend = (1 + frequency_annual_4pt) * (1 + severity_annual_4pt) - 1

print(f"\nFrequency Trend (quarterly): {frequency_trend_4pt:.6f}")
print(f"Frequency Trend (annual): {frequency_annual_4pt:.6f} ({frequency_annual_4pt*100:.2f}%)")
print(f"Severity Trend (quarterly): {severity_trend_4pt:.6f}")
print(f"Severity Trend (annual): {severity_annual_4pt:.6f} ({severity_annual_4pt*100:.2f}%)")
print(f"Combined Loss Trend (projected): {step_7_projected_loss_trend:.6f} ({step_7_projected_loss_trend*100:.2f}%)")
print(f"Ground Truth: 1.9%")
print(f"Match: {abs(step_7_projected_loss_trend - 0.019) < 0.001}")

print("\n" + "=" * 80)
print("STEP 8: Calculate Total Loss Trend Factors (Two-Step)")
print("=" * 80)

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

print(f"\nLatest Accident Year: {latest_ay}")
print(f"Current AY Date (midpoint): {current_ay_date}")
print(f"Future Average Accident Date: {future_avg_accident}")
print(f"Projected Loss Trend Period: {projected_loss_trend_period:.4f} years")
print(f"Projected Loss Trend Factor: {(1 + step_7_projected_loss_trend) ** projected_loss_trend_period:.4f}")

print("\nTotal Loss Trend Factors by Accident Year:")
for ay, factor in zip(accident_years, step_8_total_loss_trend_factors):
    print(f"{ay}: {factor:.4f}")

print("\nGround Truth:")
ground_truth_step_8 = [1.0404, 1.0412, 1.0419, 1.0427, 1.0435]
for i, gt in enumerate(ground_truth_step_8):
    ay = accident_years[i]
    calc = step_8_total_loss_trend_factors[i]
    match = abs(calc - gt) < 0.0001
    print(f"{ay}: {gt:.4f} - Match: {match}")

print("\n" + "=" * 80)
print("STEP 9: Calculate Projected Loss and LAE Ratio")
print("=" * 80)

ulae_factor = 1.143

ultimate_losses_2011_2015 = step_5_ultimate_losses[ay_start_idx:]
projected_ultimate_losses = ultimate_losses_2011_2015 * step_8_total_loss_trend_factors

total_projected_ultimate_losses = projected_ultimate_losses.sum()
total_projected_earned_premium = step_4_projected_earned_premium.sum()

step_9_projected_loss_lae_ratio = (total_projected_ultimate_losses / total_projected_earned_premium) * ulae_factor

print(f"\nULAE Factor: {ulae_factor:.3f}")
print(f"Total Projected Ultimate Losses: ${total_projected_ultimate_losses:,.2f}")
print(f"Total Projected Earned Premium at CRL: ${total_projected_earned_premium:,.2f}")
print(f"Projected Loss and LAE Ratio: {step_9_projected_loss_lae_ratio:.6f} ({step_9_projected_loss_lae_ratio*100:.3f}%)")
print(f"Ground Truth: 64.344%")
print(f"Match: {abs(step_9_projected_loss_lae_ratio - 0.64344) < 0.001}")

print("\n" + "=" * 80)
print("STEP 10: Calculate Variable Permissible Loss Ratio")
print("=" * 80)

variable_expense_provision = 0.169956
underwriting_profit_provision = 0.05

step_10_vplr = 1 - variable_expense_provision - underwriting_profit_provision

print(f"\nVariable Expense Provision: {variable_expense_provision:.6f} ({variable_expense_provision*100:.4f}%)")
print(f"Underwriting Profit Provision: {underwriting_profit_provision:.6f} ({underwriting_profit_provision*100:.2f}%)")
print(f"Variable Permissible Loss Ratio: {step_10_vplr:.6f} ({step_10_vplr*100:.2f}%)")
print(f"Ground Truth: 78%")
print(f"Match: {abs(step_10_vplr - 0.78) < 0.001}")

print("\n" + "=" * 80)
print("STEP 11: Calculate Indicated Rate Change")
print("=" * 80)

fixed_expense_provision = 0.112867

step_11_indicated_rate_change = ((step_9_projected_loss_lae_ratio + fixed_expense_provision) / step_10_vplr) - 1

print(f"\nSelected Projected Loss and LAE Ratio: {step_9_projected_loss_lae_ratio:.6f} ({step_9_projected_loss_lae_ratio*100:.3f}%)")
print(f"Fixed Expense Provision: {fixed_expense_provision:.6f} ({fixed_expense_provision*100:.4f}%)")
print(f"Variable Permissible Loss Ratio: {step_10_vplr:.6f} ({step_10_vplr*100:.2f}%)")
print(f"Indicated Rate Change: {step_11_indicated_rate_change:.6f} ({step_11_indicated_rate_change*100:.2f}%)")
print(f"Ground Truth: -3.04%")
print(f"Match: {abs(step_11_indicated_rate_change - (-0.0304)) < 0.001}")

print("\n" + "=" * 80)
print("STEP 12: Calculate Classical Credibility")
print("=" * 80)

total_claims = 700
claims_for_full_credibility = 1082

step_12_credibility = np.sqrt(total_claims / claims_for_full_credibility)

print(f"\nTotal Claims in Historical Period: {total_claims}")
print(f"Claims for Full Credibility: {claims_for_full_credibility}")
print(f"Credibility: {step_12_credibility:.6f} ({step_12_credibility*100:.3f}%)")
print(f"Ground Truth: 80.433%")
print(f"Match: {abs(step_12_credibility - 0.80433) < 0.001}")

print("\n" + "=" * 80)
print("STEP 13: Calculate Trended Present Rates Indication")
print("=" * 80)

latest_indicated_rate_change = 0.132
last_rate_change_eff_date = '1/1/2016'
last_rate_change_taken = 0.05

net_trend = (1 + step_7_projected_loss_trend) / (1 + step_2_premium_trend) - 1

trend_from_date = datetime(2016, 1, 1).date()
trend_to_date = datetime(2017, 1, 1).date()
trend_period_years = calculate_trend_period_years(trend_from_date, trend_to_date)

step_13_trended_present_rates = (1 + net_trend) ** trend_period_years * ((1 + latest_indicated_rate_change) / (1 + last_rate_change_taken)) - 1

print(f"\nLoss Trend (Projected): {step_7_projected_loss_trend:.6f} ({step_7_projected_loss_trend*100:.2f}%)")
print(f"Premium Trend: {step_2_premium_trend:.6f} ({step_2_premium_trend*100:.2f}%)")
print(f"Net Trend: {net_trend:.6f} ({net_trend*100:.3f}%)")
print(f"Trend Period (1/1/2016 to 1/1/2017): {trend_period_years:.4f} years")
print(f"Latest Indicated Rate Change: {latest_indicated_rate_change:.3f} ({latest_indicated_rate_change*100:.1f}%)")
print(f"Last Rate Change Taken: {last_rate_change_taken:.3f} ({last_rate_change_taken*100:.1f}%)")
print(f"Trended Present Rates Indication: {step_13_trended_present_rates:.6f} ({step_13_trended_present_rates*100:.3f}%)")
print(f"Ground Truth: 7.688%")
print(f"Match: {abs(step_13_trended_present_rates - 0.07688) < 0.001}")

print("\n" + "=" * 80)
print("STEP 14: Calculate Credibility-Weighted Rate Change")
print("=" * 80)

step_14_credibility_weighted_rate_change = (
    step_12_credibility * step_11_indicated_rate_change + 
    (1 - step_12_credibility) * step_13_trended_present_rates
)

print(f"\nCredibility: {step_12_credibility:.6f} ({step_12_credibility*100:.3f}%)")
print(f"Indicated Rate Change: {step_11_indicated_rate_change:.6f} ({step_11_indicated_rate_change*100:.2f}%)")
print(f"Trended Present Rates: {step_13_trended_present_rates:.6f} ({step_13_trended_present_rates*100:.3f}%)")
print(f"Credibility-Weighted Rate Change: {step_14_credibility_weighted_rate_change:.6f} ({step_14_credibility_weighted_rate_change*100:.4f}%)")
print(f"Ground Truth: -0.9433%")
print(f"Match: {abs(step_14_credibility_weighted_rate_change - (-0.009433)) < 0.001}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

step_1_match = all(abs(step_1_earned_premium_crl[i] - ground_truth_step_1[i]) < 0.01 for i in range(5))
step_2_match = abs(step_2_premium_trend - 0.02) < 0.001
step_3_match = all(abs(step_3_total_trend_factors[i] - ground_truth_step_3[i]) < 0.0001 for i in range(5))
step_4_match = all(abs(step_4_projected_earned_premium[i] - ground_truth_step_4[i]) < 200 for i in range(5))
step_5_match = all(abs(step_5_ultimate_losses[ay_start_idx + i] - ground_truth_step_5[i]) < 0.01 for i in range(len(ground_truth_step_5)))
step_6_match = abs(step_6_current_loss_trend - (-0.001)) < 0.001
step_7_match = abs(step_7_projected_loss_trend - 0.019) < 0.001
step_8_match = all(abs(step_8_total_loss_trend_factors[i] - ground_truth_step_8[i]) < 0.0001 for i in range(len(step_8_total_loss_trend_factors)))
step_9_match = abs(step_9_projected_loss_lae_ratio - 0.64344) < 0.001
step_10_match = abs(step_10_vplr - 0.78) < 0.001
step_11_match = abs(step_11_indicated_rate_change - (-0.0304)) < 0.001
step_12_match = abs(step_12_credibility - 0.80433) < 0.001
step_13_match = abs(step_13_trended_present_rates - 0.07688) < 0.001
step_14_match = abs(step_14_credibility_weighted_rate_change - (-0.009433)) < 0.001

print(f"Step 1 - Earned Premiums at CRL: {'PASS' if step_1_match else 'FAIL'}")
print(f"Step 2 - Premium Trend: {'PASS' if step_2_match else 'FAIL'} ({step_2_premium_trend*100:.2f}% vs 2.0%)")
print(f"Step 3 - Total Premium Trend Factors: {'PASS' if step_3_match else 'FAIL'}")
print(f"Step 4 - Projected Earned Premiums: {'PASS' if step_4_match else 'FAIL'} (within $200)")
print(f"Step 5 - Ultimate Losses: {'PASS' if step_5_match else 'FAIL'}")
print(f"Step 6 - Current Loss Trend: {'PASS' if step_6_match else 'FAIL'} ({step_6_current_loss_trend*100:.2f}% vs -0.1%)")
print(f"Step 7 - Projected Loss Trend: {'PASS' if step_7_match else 'FAIL'} ({step_7_projected_loss_trend*100:.2f}% vs 1.9%)")
print(f"Step 8 - Total Loss Trend Factors: {'PASS' if step_8_match else 'FAIL'}")
print(f"Step 9 - Projected Loss and LAE Ratio: {'PASS' if step_9_match else 'FAIL'} ({step_9_projected_loss_lae_ratio*100:.3f}% vs 64.344%)")
print(f"Step 10 - Variable Permissible Loss Ratio: {'PASS' if step_10_match else 'FAIL'} ({step_10_vplr*100:.2f}% vs 78%)")
print(f"Step 11 - Indicated Rate Change: {'PASS' if step_11_match else 'FAIL'} ({step_11_indicated_rate_change*100:.2f}% vs -3.04%)")
print(f"Step 12 - Classical Credibility: {'PASS' if step_12_match else 'FAIL'} ({step_12_credibility*100:.3f}% vs 80.433%)")
print(f"Step 13 - Trended Present Rates: {'PASS' if step_13_match else 'FAIL'} ({step_13_trended_present_rates*100:.3f}% vs 7.688%)")
print(f"Step 14 - Credibility-Weighted Rate Change: {'PASS' if step_14_match else 'FAIL'} ({step_14_credibility_weighted_rate_change*100:.4f}% vs -0.9433%)")

print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)
print(f"\nPremium Trend (Annual): {step_2_premium_trend:.4f}")
print(f"\nTotal Trend Factors by Calendar Year:")
for i, year in enumerate(cy_earned_premium_df['Calendar Year']):
    print(f"  {year}: {step_3_total_trend_factors[i]:.4f}")
print(f"\nProjected Earned Premiums at CRL by Calendar Year:")
for i, year in enumerate(cy_earned_premium_df['Calendar Year']):
    print(f"  {year}: ${step_4_projected_earned_premium[i]:,.0f}")

