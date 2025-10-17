import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent
# Data file paths
data_path_1 = data_dir / 'current_level_earned_premium.csv'
data_path_2 = data_dir / 'reported_claims_triangle.csv'

### STEP 1: Load Triangle Data
# Write your code below to load and convert the triangle data
