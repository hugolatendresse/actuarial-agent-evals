import pandas as pd
import numpy as np
import chainladder as cl
from pathlib import Path

data_dir = Path(__file__).resolve().parent
reported_count_data_path = data_dir / 'reported_claim_count_triangle.csv'

### STEP 1: Develop Reported Count to Ultimate

