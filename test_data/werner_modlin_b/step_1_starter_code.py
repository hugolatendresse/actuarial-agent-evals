import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'test_data' / 'werner_modlin_b'

state_data = pd.read_csv(data_dir / 'state_earned_exposures_and_reported_loss_paid_alae.csv', thousands=',')
regional_qtrly_pp = pd.read_csv(data_dir / 'regional_quarterly_paid_pure_premium_with_alae.csv', thousands=',')
triangle_df = pd.read_csv(data_dir / 'countrywide_reported_loss_paid_alae_triangle.csv', thousands=',')

### STEP 1: Develop State Losses to Ultimate using Countrywide LDFs


