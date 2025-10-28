import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


SOLUTION_FILENAME = "step_solution.py"


def validate_step_1(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'disposal_rate_tri' in dir(), "Variable 'disposal_rate_tri' not found"

if hasattr(disposal_rate_tri, 'values'):
    ay_2001_idx = 0
    for j in range(min(9, disposal_rate_tri.shape[3])):
        val = disposal_rate_tri.values[0, 0, ay_2001_idx, j]
        if not np.isnan(val):
            print(f"DR_2001_{j}: {val:.5f}")
else:
    print("ERROR: disposal_rate_tri is not a Triangle")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    
    try:
        disposal_rates_2001 = []
        for line in output.split('\n'):
            if line.startswith('DR_2001_'):
                val = float(line.split(':')[1].strip())
                disposal_rates_2001.append(val)
        
        if len(disposal_rates_2001) < 4:
            return {"passed": False, "error": f"Expected at least 4 disposal rate values for AY 2001, got {len(disposal_rates_2001)}"}
        
        expected_rates = [0.208935, 0.468041, 0.643299, 0.750515, 0.841924, 0.932646, 0.984192, 0.993814]
        
        passed = all(np.isclose(a, b, rtol=0.01, atol=0.001) for a, b in zip(disposal_rates_2001[:len(expected_rates)], expected_rates[:len(disposal_rates_2001)]))
        
        return {
            "passed": passed,
            "error": None if passed else "Disposal rate values don't match expected pattern",
            "disposal_rates_2001": disposal_rates_2001
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'selected_disposal_rates' in dir() or 'selected_disposal_rates_output' in dir(), "Variable 'selected_disposal_rates' not found"

if 'selected_disposal_rates' in dir():
    rates = selected_disposal_rates
elif 'selected_disposal_rates_output' in dir():
    rates = selected_disposal_rates_output

for i, val in enumerate(rates):
    print(f"DR_{i}: {val:.5f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_rates = ground_truth["step_2"]["selected_disposal_rates"]
    
    try:
        rates = []
        for line in output.split('\n'):
            if line.startswith('DR_'):
                val = float(line.split(':')[1].strip())
                rates.append(val)
        
        if len(rates) != len(gt_rates):
            return {"passed": False, "error": f"Expected {len(gt_rates)} disposal rates, got {len(rates)}"}
        
        passed = all(np.isclose(a, b, rtol=0.01, atol=0.001) for a, b in zip(rates, gt_rates))
        
        return {
            "passed": passed,
            "error": None if passed else "Disposal rates don't match ground truth",
            "disposal_rates": rates
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'projected_incremental_cwp' in dir(), "Variable 'projected_incremental_cwp' not found"

ay_2008_idx = 7
for j, val in enumerate(projected_incremental_cwp[ay_2008_idx, :9]):
    print(f"CWP_{j}: {val:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_counts = ground_truth["step_3"]["projected_cwp_counts_2008"]
    
    try:
        counts = []
        for line in output.split('\n'):
            if line.startswith('CWP_'):
                val = float(line.split(':')[1].strip())
                counts.append(val)
        
        if len(counts) != len(gt_counts):
            return {"passed": False, "error": f"Expected {len(gt_counts)} count values, got {len(counts)}"}
        
        passed = all(np.isclose(a, b, rtol=0.05, atol=2) for a, b in zip(counts, gt_counts))
        
        return {
            "passed": passed,
            "error": None if passed else "Projected CWP counts don't match ground truth",
            "projected_counts_2008": counts
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'incremental_severity_tri' in dir(), "Variable 'incremental_severity_tri' not found"

ay_2008_idx = 7
if hasattr(incremental_severity_tri, 'values'):
    sev_2008_age12 = incremental_severity_tri.values[0, 0, ay_2008_idx, 0]
elif hasattr(incremental_severity_tri, 'shape'):
    sev_2008_age12 = incremental_severity_tri[ay_2008_idx, 0]
else:
    sev_2008_age12 = 0

print(f"SEV_2008_AGE12: {sev_2008_age12:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_sev = ground_truth["step_4"]["incremental_severity_2008_age_12"]
    
    if "SEV_2008_AGE12:" in output:
        sev_str = output.split("SEV_2008_AGE12:")[1].strip().split()[0]
        actual_sev = float(sev_str)
        
        passed = np.isclose(actual_sev, gt_sev, rtol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_sev:,.2f}, got {actual_sev:,.2f}",
            "incremental_severity_2008_age_12": actual_sev
        }
    
    return {"passed": False, "error": "Could not parse incremental_severity from output"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'adjusted_severity' in dir(), "Variable 'adjusted_severity' not found"

ay_2008_idx = 7
ay_2007_idx = 6

if isinstance(adjusted_severity, np.ndarray):
    sev_2008_age12 = adjusted_severity[ay_2008_idx, 0]
    sev_2007_age12 = adjusted_severity[ay_2007_idx, 0]
else:
    sev_2008_age12 = 0
    sev_2007_age12 = 0

print(f"ADJ_SEV_2008_AGE12: {sev_2008_age12:.2f}")
print(f"ADJ_SEV_2007_AGE12: {sev_2007_age12:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_sev_2008 = ground_truth["step_5"]["adjusted_severity_2008_age_12"]
    gt_sev_2007 = ground_truth["step_5"]["adjusted_severity_2007_age_12"]
    
    try:
        sev_2008 = None
        sev_2007 = None
        
        for line in output.split('\n'):
            if 'ADJ_SEV_2008_AGE12:' in line:
                sev_2008 = float(line.split(':')[1].strip())
            elif 'ADJ_SEV_2007_AGE12:' in line:
                sev_2007 = float(line.split(':')[1].strip())
        
        if sev_2008 is None or sev_2007 is None:
            return {"passed": False, "error": "Could not parse adjusted severities from output"}
        
        match_2008 = np.isclose(sev_2008, gt_sev_2008, rtol=0.01)
        match_2007 = np.isclose(sev_2007, gt_sev_2007, rtol=0.01)
        
        passed = match_2008 and match_2007
        
        return {
            "passed": passed,
            "error": None if passed else "Adjusted severities don't match ground truth",
            "adjusted_severity_2008_age_12": sev_2008,
            "adjusted_severity_2007_age_12": sev_2007
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_6(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'selected_adjusted_severities' in dir(), "Variable 'selected_adjusted_severities' not found"

for i, val in enumerate(selected_adjusted_severities):
    print(f"SEV_{i}: {val:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_severities = ground_truth["step_6"]["selected_adjusted_severities"]
    
    try:
        severities = []
        for line in output.split('\n'):
            if line.startswith('SEV_'):
                val = float(line.split(':')[1].strip())
                severities.append(val)
        
        if len(severities) != len(gt_severities):
            return {"passed": False, "error": f"Expected {len(gt_severities)} severities, got {len(severities)}"}
        
        passed = all(np.isclose(a, b, rtol=0.01) for a, b in zip(severities, gt_severities))
        
        return {
            "passed": passed,
            "error": None if passed else "Selected severities don't match ground truth",
            "selected_adjusted_severities": severities
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_7(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'tail_severity_72' in dir(), "Variable 'tail_severity_72' not found"
assert 'tail_severity_84' in dir(), "Variable 'tail_severity_84' not found"

print(f"TAIL_72: {tail_severity_72:.2f}")
print(f"TAIL_84: {tail_severity_84:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_tail_72 = ground_truth["step_7"]["tail_severity_72_plus"]
    gt_tail_84 = ground_truth["step_7"]["tail_severity_84_plus"]
    
    try:
        tail_72 = None
        tail_84 = None
        
        for line in output.split('\n'):
            if 'TAIL_72:' in line:
                tail_72 = float(line.split(':')[1].strip())
            elif 'TAIL_84:' in line:
                tail_84 = float(line.split(':')[1].strip())
        
        if tail_72 is None or tail_84 is None:
            return {"passed": False, "error": "Could not parse tail severities from output"}
        
        match_72 = np.isclose(tail_72, gt_tail_72, rtol=0.01)
        match_84 = np.isclose(tail_84, gt_tail_84, rtol=0.01)
        
        passed = match_72 and match_84
        
        return {
            "passed": passed,
            "error": None if passed else "Tail severities don't match ground truth",
            "tail_severity_72_plus": tail_72,
            "tail_severity_84_plus": tail_84
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_8(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'full_selected_severities' in dir(), "Variable 'full_selected_severities' not found"

for i, val in enumerate(full_selected_severities):
    print(f"FULL_SEV_{i}: {val:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_severities = ground_truth["step_8"]["full_selected_severities"]
    
    try:
        severities = []
        for line in output.split('\n'):
            if line.startswith('FULL_SEV_'):
                val = float(line.split(':')[1].strip())
                severities.append(val)
        
        if len(severities) != len(gt_severities):
            return {"passed": False, "error": f"Expected {len(gt_severities)} severities, got {len(severities)}"}
        
        passed = all(np.isclose(a, b, rtol=0.01) for a, b in zip(severities, gt_severities))
        
        return {
            "passed": passed,
            "error": None if passed else "Full severities don't match ground truth",
            "full_selected_severities": severities
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_9(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'projected_incremental_paid' in dir(), "Variable 'projected_incremental_paid' not found"

ay_2001_idx = 0
for j, val in enumerate(projected_incremental_paid[ay_2001_idx, :9]):
    print(f"PAID_{j}: {val:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_paid = ground_truth["step_9"]["projected_paid_2001"]
    
    try:
        paid = []
        for line in output.split('\n'):
            if line.startswith('PAID_'):
                val = float(line.split(':')[1].strip())
                paid.append(val)
        
        if len(paid) != len(gt_paid):
            return {"passed": False, "error": f"Expected {len(gt_paid)} paid values, got {len(paid)}"}
        
        passed = all(np.isclose(a, b, rtol=0.05, atol=10) for a, b in zip(paid, gt_paid))
        
        return {
            "passed": passed,
            "error": None if passed else "Projected paid amounts don't match ground truth",
            "projected_paid_2001": paid
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_10(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_ultimates_by_ay' in dir() or 'ultimates_by_ay' in dir(), "Variable 'total_ultimates_by_ay' not found"

if 'total_ultimates_by_ay' in dir():
    ultimates = total_ultimates_by_ay
elif 'ultimates_by_ay' in dir():
    ultimates = ultimates_by_ay

for i, val in enumerate(ultimates):
    print(f"ULT_{2001+i}: {val:.2f}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)
    
    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    output = result.stdout
    gt_ultimates = ground_truth["step_10"]["total_ultimates_by_ay"]
    
    try:
        ultimates = []
        for line in output.split('\n'):
            if line.startswith('ULT_'):
                val = float(line.split(':')[1].strip())
                ultimates.append(val)
        
        if len(ultimates) != len(gt_ultimates):
            return {"passed": False, "error": f"Expected {len(gt_ultimates)} ultimates, got {len(ultimates)}"}
        
        passed = all(np.isclose(a, b, rtol=0.01, atol=50) for a, b in zip(ultimates, gt_ultimates))
        
        return {
            "passed": passed,
            "error": None if passed else "Total ultimates don't match ground truth",
            "total_ultimates_by_ay": ultimates
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}

