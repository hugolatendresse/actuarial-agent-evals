import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

script_dir = Path(__file__).resolve().parent
if "ide_results" in str(script_dir):
    project_root = script_dir.parent.parent.parent
    data_dir = project_root / "test_data" / "friedland_xyz_fs1_method"
else:
    data_dir = script_dir
cwp_count_data_path = data_dir / 'closed_with_pay_claim_count_triangle.csv'
reported_count_data_path = data_dir / 'reported_claim_count_triangle.csv'

### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###

cwp_count_df = pd.read_csv(cwp_count_data_path, thousands=',')

cwp_count_long = cwp_count_df.melt(id_vars=['Accident Year'], var_name='age', value_name='value')
cwp_count_long = cwp_count_long.dropna()
cwp_count_long['age'] = cwp_count_long['age'].astype(int)
cwp_count_long['origin_period'] = pd.PeriodIndex(cwp_count_long['Accident Year'].astype(int).astype(str), freq='Y')
cwp_count_long['valuation'] = (cwp_count_long['origin_period'] + (cwp_count_long['age'].astype(int) // 12) - 1).dt.to_timestamp(how='end')

cwp_count_tri = cl.Triangle(
    cwp_count_long,
    origin='Accident Year',
    development='valuation',
    columns=['value'],
    cumulative=True
)

cwp_pipe = cl.Pipeline(steps=[
    ('dev', cl.Development(average='volume', n_periods=4)),
    ('tail', cl.TailConstant(tail=1.00)),
    ('model', cl.Chainladder())
])

cwp_pipe.fit(cwp_count_tri)
cwp_ultimate = cwp_pipe.named_steps.model.ultimate_
cwp_count_ultimate = cwp_ultimate.sum().sum()

