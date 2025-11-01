import pandas as pd
import numpy as np
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'werner_modlin_a'

cy_earned_premium_df = pd.read_csv(data_dir / 'cy_earned_premium.csv', thousands=',')
cy_earned_exposures_df = pd.read_csv(data_dir / 'cy_earned_exposures.csv', thousands=',')
qtrly_written_premium_exposures_df = pd.read_csv(data_dir / 'qtrly_written_premium_exposures.csv', thousands=',')

cy_earned_premium_df['Earned Premium at CRL'] = (
    cy_earned_premium_df['Earned Premium'] * 
    cy_earned_premium_df['Current Rate Level Factor']
)

step_1_earned_premium_crl = cy_earned_premium_df['Earned Premium at CRL'].values

### STEP 2: Calculate 8-Point Exponential Trend for Average Written Premium at CRL

