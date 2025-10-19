import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent
# Data file paths
triangle_data_path = data_dir / 'reported_claims_triangle.csv'
premium_data_path = data_dir / 'earned_premium.csv'
rate_changes_data_path = data_dir / 'rate_changes.csv'
claim_ratio_data_path = data_dir / 'expected_claim_ratio.csv'

### STEP 1: Calculate Current Level Earned Premium
# Load premium and rate change data, then calculate current level earned premium

