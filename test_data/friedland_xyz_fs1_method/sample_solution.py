import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent

reported_claims_df = pd.read_csv(data_dir / 'reported_claims_triangle.csv', thousands=',')
reported_count_df = pd.read_csv(data_dir / 'reported_claim_count_triangle.csv', thousands=',')
cwp_count_df = pd.read_csv(data_dir / 'closed_with_pay_claim_count_triangle.csv', thousands=',')

reported_claims_long = reported_claims_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
reported_claims_long = reported_claims_long.dropna()
reported_claims_long['age'] = reported_claims_long['age'].astype(int)
reported_claims_long['origin_period'] = pd.PeriodIndex(reported_claims_long['Accident Year'].astype(int).astype(str), freq='Y')
reported_claims_long['valuation'] = (reported_claims_long['origin_period'] + (reported_claims_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

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

reported_claims_tri = cl.Triangle(
    reported_claims_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

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

print("=" * 80)
print("STEP 1: Develop CWP Count Triangle to Ultimate")
print("=" * 80)

cwp_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

cwp_pipe.fit(cwp_count_tri)
cwp_ultimate = cwp_pipe.named_steps.model.ultimate_
cwp_total_ultimate = cwp_ultimate.sum().sum()

print(f"\nCWP Link Ratios (LDF): {cwp_pipe.named_steps.dev.ldf_.values[0, 0, 0, :]}")
print(f"CWP Total Ultimate: {cwp_total_ultimate:,.0f}")
print(f"Ground Truth: 13,863")
print(f"Match: {abs(cwp_total_ultimate - 13863) < 10}")

print("\n" + "=" * 80)
print("STEP 2: Develop Reported Count Triangle to Ultimate")
print("=" * 80)

reported_count_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

reported_count_pipe.fit(reported_count_tri)
reported_count_ultimate = reported_count_pipe.named_steps.model.ultimate_
reported_count_total_ultimate = reported_count_ultimate.sum().sum()

print(f"\nReported Count Link Ratios (LDF): {reported_count_pipe.named_steps.dev.ldf_.values[0, 0, 0, :]}")
print(f"Reported Count Total Ultimate: {reported_count_total_ultimate:,.0f}")
print(f"Ground Truth: 16,335")
print(f"Match: {abs(reported_count_total_ultimate - 16335) < 10}")

print("\n" + "=" * 80)
print("STEP 3: Calculate AY Ultimates (Average of CWP and Reported)")
print("=" * 80)

cwp_ultimates_by_ay = cwp_ultimate.values[0, 0, :, -1]
reported_count_ultimates_by_ay = reported_count_ultimate.values[0, 0, :, -1]

ay_ultimates = (cwp_ultimates_by_ay + reported_count_ultimates_by_ay) / 2

ground_truth_ay = [637, 1047, 1416, 1467, 1569, 1668, 2319, 2507, 1852, 1659, 1696]

print("\nAccident Year Ultimates:")
matches = []
for i, (calc, gt) in enumerate(zip(ay_ultimates, ground_truth_ay)):
    year = 1998 + i
    match = abs(calc - gt) < 1
    matches.append(match)
    print(f"{year}: {calc:,.0f} (Ground Truth: {gt:,}) {'✓' if match else 'X'}")
    
print(f"\nAll match: {all(matches)}")
print(f"Total: {ay_ultimates.sum():,.0f}")

print("\n" + "=" * 80)
print("STEP 4: Project Ultimate Reported Severity")
print("=" * 80)

severity_tri = reported_claims_tri / reported_count_tri

severity_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='simple', n_periods=5)),
    ('tail', cl.TailConstant(tail=1.01)),
    ('model', cl.Chainladder())
])

severity_pipe.fit(severity_tri)
severity_ultimate = severity_pipe.named_steps.model.ultimate_

ultimate_severity_values = severity_ultimate.values[0, 0, :, -1]
ultimate_amounts = ultimate_severity_values * ay_ultimates

total_ultimate_from_severity = ultimate_amounts.sum()

print(f"\nSeverity Link Ratios (LDF): {severity_pipe.named_steps.dev.ldf_.values[0, 0, 0, :]}")
print(f"Total Ultimate from Severity Method: {total_ultimate_from_severity:,.0f}")
print(f"Ground Truth: 689,610,000")
print(f"Match: {abs(total_ultimate_from_severity - 689610000) < 1000}")

print("\n" + "=" * 80)
print("STEP 5: Calculate Total Ultimate and IBNR")
print("=" * 80)

latest_reported_claims = reported_claims_tri.latest_diagonal.sum().sum()
ibnr = total_ultimate_from_severity - latest_reported_claims

print(f"\nLatest Reported Claims: {latest_reported_claims:,.0f}")
print(f"Total Ultimate: {total_ultimate_from_severity:,.0f}")
print(f"IBNR: {ibnr:,.0f}")
print(f"\nGround Truth Ultimate: 689,610,000")
print(f"Ground Truth IBNR: 239,984,000")
print(f"Ultimate Match: {abs(total_ultimate_from_severity - 689610000) < 1000}")
print(f"IBNR Match: {abs(ibnr - 239984000) < 1000}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Step 1 CWP Ultimate: {cwp_total_ultimate:,.0f} (Target: 13,863) {abs(cwp_total_ultimate - 13863) < 10}")
print(f"Step 2 Reported Count Ultimate: {reported_count_total_ultimate:,.0f} (Target: 16,335) {abs(reported_count_total_ultimate - 16335) < 10}")
print(f"Step 3 AY Ultimates: {all(matches)}")
print(f"Step 4 Total Ultimate: {total_ultimate_from_severity:,.0f} (Target: 689,610,000) {abs(total_ultimate_from_severity - 689610000) < 1000}")
print(f"Step 5 IBNR: {ibnr:,.0f} (Target: 239,984,000) {abs(ibnr - 239984000) < 1000}")
