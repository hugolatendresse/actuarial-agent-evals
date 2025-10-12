import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

# Data file paths
triangle_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/reported_claims_triangle.csv'
premium_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/earned_premium.csv'
rate_changes_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/rate_changes.csv'
claim_ratio_data_path = r'/Users/sabrinatan/code/aria-tests/test_data/friedland_xyz_cc_method/expected_claim_ratio.csv'

### STEP 1: Calculate Current Level Earned Premium
# Load premium and rate change data, then calculate current level earned premium

