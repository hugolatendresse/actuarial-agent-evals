import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent

reported_count_df = pd.read_csv(data_dir / 'reported_claim_count_triangle.csv')
cwp_count_df = pd.read_csv(data_dir / 'closed_with_pay_claim_count_triangle.csv')
paid_claims_df = pd.read_csv(data_dir / 'cumulative_paid_claims.csv')

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

print("=" * 80)
print("STEP 1: Develop Reported Count Triangle and Build Disposal Rate Triangle")
print("=" * 80)

reported_count_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

reported_count_pipe.fit(reported_count_tri)
reported_count_ultimate = reported_count_pipe.named_steps.model.ultimate_

print(f"\nReported Count Link Ratios (LDF): {reported_count_pipe.named_steps.dev.ldf_.values[0, 0, 0, :]}")
print(f"\nReported Count Ultimate Values by AY:")
for i, ay in enumerate(range(2001, 2009)):
    ult = reported_count_ultimate.values[0, 0, i, -1]
    print(f"{ay}: {ult:.0f}")

disposal_rate_tri = cwp_count_tri / reported_count_ultimate

print("\nDisposal Rate Triangle:")
disposal_rate_array = disposal_rate_tri.values[0, 0, :, :]
ages_list = list(range(12, 12 + disposal_rate_array.shape[1] * 12, 12))
disposal_df = pd.DataFrame(disposal_rate_array, 
                          index=range(2001, 2001+disposal_rate_array.shape[0]), 
                          columns=ages_list)
print(disposal_df.to_string())

print("\n" + "=" * 80)
print("STEP 2: Select Disposal Rates by Age")
print("=" * 80)

selected_disposal_rates_output = []
n_periods = 2
target_ages = [12, 24, 36, 48, 60, 72, 84, 96, 108]

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

print(f"\nSelected Disposal Rates by Age:")
for i, rate in enumerate(selected_disposal_rates_output):
    print(f"Age {target_ages[i]}: {rate:.5f}")

print(f"\nGround Truth: [0.244, 0.577, 0.709, 0.818, 0.912, 0.953, 0.983, 0.994, 1.000]")

print("\n" + "=" * 80)
print("STEP 3: Calculate Projected Incremental Closed with Payment Claim Count")
print("=" * 80)

cwp_incremental = cwp_count_tri.cum_to_incr()
latest_cwp_by_ay = cwp_count_tri.latest_diagonal.values[0, 0, :, 0]
ultimate_reported_by_ay = reported_count_ultimate.values[0, 0, :, -1]

n_origins = len(latest_cwp_by_ay)
n_dev = len(selected_disposal_rates_output)

projected_incremental_cwp = np.zeros((n_origins, n_dev))

cwp_incremental_array = cwp_incremental.values[0, 0, :, :]
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

print("\nProjected Incremental Closed with Payment Claim Count Triangle:")
main_ages = [12, 24, 36, 48, 60, 72, 84, 96]
projected_df = pd.DataFrame(projected_incremental_cwp[:, :len(main_ages)], 
                            index=range(2001, 2001+n_origins), 
                            columns=main_ages)
projected_df['To Ult'] = projected_incremental_cwp[:, -1]
print(projected_df.to_string())

print("\n" + "=" * 80)
print("STEP 4: Calculate Incremental Paid Severity Triangle")
print("=" * 80)

paid_incremental = paid_claims_tri.cum_to_incr()
cwp_incremental_from_cum = cwp_count_tri.cum_to_incr()

incremental_severity_tri = paid_incremental / cwp_incremental_from_cum

print("\nIncremental Paid Severity Triangle:")
severity_array = incremental_severity_tri.values[0, 0, :, :]
severity_cols = list(range(12, 12 + severity_array.shape[1] * 12, 12))
severity_display_df = pd.DataFrame(severity_array, 
                                  index=range(2001, 2001+severity_array.shape[0]), 
                                  columns=severity_cols)
print(severity_display_df.to_string())

print("\n" + "=" * 80)
print("STEP 5: Calculate Adjusted to 2008 Incremental Paid Severity Triangle")
print("=" * 80)

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

adjusted_severity_df = pd.DataFrame(adjusted_severity,
                                   index=range(2001, 2001+n_origins),
                                   columns=severity_cols)
print("\nAdjusted to 2008 Incremental Paid Severity Triangle:")
print(adjusted_severity_df.to_string())

print("\n" + "=" * 80)
print("STEP 6: Select Adjusted Incremental Paid Severities (Ages 12-60)")
print("=" * 80)

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

print(f"\nSelected Adjusted Incremental Paid Severities (12-60):")
for i, sev in enumerate(selected_adjusted_severities):
    ages_display = [12, 24, 36, 48, 60]
    gt_values = [11807, 15167, 26049, 35182, 41910]
    print(f"Age {ages_display[i]}: {sev:,.0f} (Ground Truth: {gt_values[i] * 1000:,.0f})")
print(f"Ground Truth (in thousands): [11,807, 15,167, 26,049, 35,182, 41,910]")

print("\n" + "=" * 80)
print("STEP 7: Calculate Tail Severities for Ages 72+ and 84+")
print("=" * 80)

total_cwp_72_plus = 0
total_paid_72_plus = 0
total_cwp_84_plus = 0
total_paid_84_plus = 0

for i in range(n_origins):
    ay = 2001 + i
    years_to_trend = base_year - ay
    
    if ay >= 2007:
        tort_reform_factor = 1.0
    elif ay == 2006:
        tort_reform_factor = (1 - 0.33) / (1 - 0.107)
    else:
        tort_reform_factor = 1 - 0.33
    
    for j in range(5, severity_array.shape[1]):
        age = severity_cols[j]
        
        if j < severity_array.shape[1]:
            cwp_val = cwp_incremental_from_cum.values[0, 0, i, j] if not np.isnan(cwp_incremental_from_cum.values[0, 0, i, j]) else 0
            paid_val = paid_incremental.values[0, 0, i, j] if not np.isnan(paid_incremental.values[0, 0, i, j]) else 0
            
            adjusted_paid_val = paid_val * (severity_trend ** years_to_trend) * tort_reform_factor
            
            if age >= 72:
                total_cwp_72_plus += cwp_val
                total_paid_72_plus += adjusted_paid_val
            
            if age >= 84:
                total_cwp_84_plus += cwp_val
                total_paid_84_plus += adjusted_paid_val

tail_severity_72 = total_paid_72_plus / total_cwp_72_plus if total_cwp_72_plus > 0 else 0
tail_severity_84 = total_paid_84_plus / total_cwp_84_plus if total_cwp_84_plus > 0 else 0

print(f"\nTail Severity 72+: {tail_severity_72:,.0f}")
print(f"Ground Truth: {59951 * 1000:,.0f}")
print(f"Tail Severity 84+: {tail_severity_84:,.0f}")
print(f"Ground Truth: {70424 * 1000:,.0f}")

print("\n" + "=" * 80)
print("STEP 8: Full Array of Selected Adjusted Incremental Paid Severities")
print("=" * 80)

full_selected_severities = selected_adjusted_severities + [tail_severity_72, tail_severity_84, tail_severity_84, tail_severity_84]

print(f"\nFull Selected Adjusted Incremental Paid Severities (12 to 108-Ult):")
all_ages = [12, 24, 36, 48, 60, 72, 84, 96, '108-Ult']
for age, sev in zip(all_ages, full_selected_severities):
    print(f"Age {age}: {sev:,.0f}")

print(f"\nGround Truth (x1000): 11,807 | 15,167 | 26,049 | 35,182 | 41,910 | 59,951 | 70,424 | 70,424 | 70,424")

print("\n" + "=" * 80)
print("STEP 9: Project Unadjusted Incremental Paid Severities")
print("=" * 80)

projected_unadjusted_severity = np.zeros((n_origins, len(full_selected_severities)))

for i in range(n_origins):
    ay = 2001 + i
    years_to_trend = base_year - ay
    
    if ay >= 2007:
        tort_reform_factor = 1.0
    elif ay == 2006:
        tort_reform_factor = (1 - 0.33) / (1 - 0.107)
    else:
        tort_reform_factor = 1 - 0.33
    
    for j in range(len(full_selected_severities)):
        if j < severity_array.shape[1] and not np.isnan(severity_array[i, j]):
            projected_unadjusted_severity[i, j] = severity_array[i, j]
        else:
            adjusted_severity_selected = full_selected_severities[j]
            unadjusted = adjusted_severity_selected / (severity_trend ** years_to_trend) / tort_reform_factor
            projected_unadjusted_severity[i, j] = unadjusted

projected_incremental_paid = np.zeros((n_origins, len(full_selected_severities)))

for i in range(n_origins):
    for j in range(len(full_selected_severities)):
        severity = projected_unadjusted_severity[i, j]
        count = projected_incremental_cwp[i, j] if j < projected_incremental_cwp.shape[1] else projected_incremental_cwp[i, -1]
        projected_incremental_paid[i, j] = severity * count / 1000

print("\nProjected Unadjusted Incremental Paid (in thousands):")
display_cols = [12, 24, 36, 48, 60, 72, 84, 96, '108-Ult']
projected_unadj_df = pd.DataFrame(projected_incremental_paid,
                                 index=range(2001, 2001+n_origins),
                                 columns=display_cols)
print(projected_unadj_df.to_string())

print("\n" + "=" * 80)
print("STEP 10: Project Total Ultimates by AY")
print("=" * 80)

ultimates_by_ay = projected_incremental_paid.sum(axis=1)

print("\nTotal Ultimates by Accident Year (in thousands):")
ground_truth_ultimates = [39191, 46708, 44290, 71108, 70534, 48974, 31253, 29656]
for i, (calc, gt) in enumerate(zip(ultimates_by_ay, ground_truth_ultimates)):
    year = 2001 + i
    print(f"{year}: {calc:,.0f} (Ground Truth: {gt:,})")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Step 2 Selected Disposal Rates: {selected_disposal_rates_output}")
print(f"Step 6 Selected Adjusted Severities (12-60): {[f'{s:,.0f}' for s in selected_adjusted_severities]}")
print(f"Step 7 Tail Severity 72+: {tail_severity_72:,.0f}")
print(f"Step 7 Tail Severity 84+: {tail_severity_84:,.0f}")
print(f"Step 10 Total Ultimates: {[f'{u:,.0f}' for u in ultimates_by_ay]}")

