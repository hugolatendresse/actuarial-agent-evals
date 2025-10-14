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
assert 'cwp_count_ultimate' in dir(), "Variable 'cwp_count_ultimate' not found"

# Handle both scalar and Triangle types
if hasattr(cwp_count_ultimate, 'sum'):
    cwp_total = float(cwp_count_ultimate.sum().sum())
else:
    cwp_total = float(cwp_count_ultimate)

print(f"CWP_COUNT_ULTIMATE: {cwp_total:.2f}")
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
    gt_total = ground_truth["step_1"]["cwp_count_ultimate"]
    
    if "CWP_COUNT_ULTIMATE:" in output:
        total_str = output.split("CWP_COUNT_ULTIMATE:")[1].strip().split()[0]
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "cwp_count_ultimate": actual_total
        }
    
    return {"passed": False, "error": "Could not parse cwp_count_ultimate from output"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'reported_count_ultimate' in dir(), "Variable 'reported_count_ultimate' not found"

# Handle both scalar and Triangle types
if hasattr(reported_count_ultimate, 'sum'):
    reported_total = float(reported_count_ultimate.sum().sum())
else:
    reported_total = float(reported_count_ultimate)

print(f"REPORTED_COUNT_ULTIMATE: {reported_total:.2f}")
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
    gt_total = ground_truth["step_2"]["reported_count_ultimate"]
    
    if "REPORTED_COUNT_ULTIMATE:" in output:
        total_str = output.split("REPORTED_COUNT_ULTIMATE:")[1].strip().split()[0]
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "reported_count_ultimate": actual_total
        }
    
    return {"passed": False, "error": "Could not parse reported_count_ultimate from output"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ay_ultimates' in dir(), "Variable 'ay_ultimates' not found"
assert 'total_frequency' in dir(), "Variable 'total_frequency' not found"

print(f"TOTAL_FREQUENCY: {total_frequency:.2f}")
for i, val in enumerate(ay_ultimates):
    print(f"AY_{1998+i}: {val:.2f}")
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
    gt_total = ground_truth["step_3"]["total_frequency"]
    gt_ay_ultimates = ground_truth["step_3"]["ay_ultimates"]
    
    try:
        total_frequency = None
        ay_ultimates = []
        
        for line in output.split('\n'):
            if 'TOTAL_FREQUENCY:' in line:
                total_frequency = float(line.split(':')[1].strip())
            elif line.startswith('AY_'):
                ay_value = float(line.split(':')[1].strip())
                ay_ultimates.append(ay_value)
        
        if total_frequency is None:
            return {"passed": False, "error": "Could not parse total_frequency from output"}
        
        total_match = np.isclose(total_frequency, gt_total, rtol=0.01)
        ay_match = len(ay_ultimates) == len(gt_ay_ultimates) and all(
            np.isclose(a, b, rtol=0.01) for a, b in zip(ay_ultimates, gt_ay_ultimates)
        )
        
        passed = total_match and ay_match
        
        errors = []
        if not total_match:
            errors.append(f"Total frequency: expected {gt_total:,.2f}, got {total_frequency:,.2f}")
        if not ay_match:
            errors.append(f"AY ultimates mismatch")
        
        return {
            "passed": passed,
            "error": None if passed else "; ".join(errors),
            "total_frequency": total_frequency,
            "ay_ultimates": ay_ultimates
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ultimate_severity' in dir(), "Variable 'ultimate_severity' not found"

# Handle both scalar and Triangle types
if hasattr(ultimate_severity, 'sum'):
    sev_total = float(ultimate_severity.sum().sum())
else:
    sev_total = float(ultimate_severity)

print(f"ULTIMATE_SEVERITY: {sev_total:.2f}")
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
    gt_total = ground_truth["step_4"]["ultimate_severity"]
    
    if "ULTIMATE_SEVERITY:" in output:
        total_str = output.split("ULTIMATE_SEVERITY:")[1].strip().split()[0]
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "ultimate_severity": actual_total
        }
    
    return {"passed": False, "error": "Could not parse ultimate_severity from output"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_ultimate' in dir(), "Variable 'total_ultimate' not found"
assert 'total_ibnr' in dir(), "Variable 'total_ibnr' not found"

# Handle both scalar and Triangle types
if hasattr(total_ultimate, 'sum'):
    ult_val = float(total_ultimate.sum().sum())
else:
    ult_val = float(total_ultimate)

if hasattr(total_ibnr, 'sum'):
    ibnr_val = float(total_ibnr.sum().sum())
else:
    ibnr_val = float(total_ibnr)

print(f"TOTAL_ULTIMATE: {ult_val:.2f}")
print(f"TOTAL_IBNR: {ibnr_val:.2f}")
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
    gt_ultimate = ground_truth["step_5"]["total_ultimate"]
    gt_ibnr = ground_truth["step_5"]["total_ibnr"]
    
    try:
        total_ultimate = None
        total_ibnr = None
        
        for line in output.split('\n'):
            if 'TOTAL_ULTIMATE:' in line:
                total_ultimate = float(line.split(':')[1].strip().split()[0])
            elif 'TOTAL_IBNR:' in line:
                total_ibnr = float(line.split(':')[1].strip().split()[0])
        
        if total_ultimate is None or total_ibnr is None:
            return {"passed": False, "error": "Could not parse total_ultimate or total_ibnr from output"}
        
        ultimate_match = np.isclose(total_ultimate, gt_ultimate, rtol=0.001)
        ibnr_match = np.isclose(total_ibnr, gt_ibnr, rtol=0.001)
        
        passed = ultimate_match and ibnr_match
        
        errors = []
        if not ultimate_match:
            errors.append(f"Total ultimate: expected {gt_ultimate:,.2f}, got {total_ultimate:,.2f}")
        if not ibnr_match:
            errors.append(f"Total IBNR: expected {gt_ibnr:,.2f}, got {total_ibnr:,.2f}")
        
        return {
            "passed": passed,
            "error": None if passed else "; ".join(errors),
            "total_ultimate": total_ultimate,
            "total_ibnr": total_ibnr
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}

