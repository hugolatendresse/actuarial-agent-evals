import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


SOLUTION_FILENAME = "step_solution.py"


def validate_step_1(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 1 output."""
    result = subprocess.run(
        ["python", SOLUTION_FILENAME],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}
    
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

assert 'triangle' in dir(), "Variable 'triangle' not found"
print(f"SHAPE: {triangle.shape}")
print(f"ORIGINS: {len(triangle.origin)}")
print(f"DEVELOPMENT: {len(triangle.development)}")
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
    
    output = result.stdout
    gt = ground_truth["step_1"]
    
    passed = True
    errors = []
    
    if f"ORIGINS: {len(gt['origins'])}" not in output:
        passed = False
        errors.append(f"Expected {len(gt['origins'])} origins")
    
    if f"DEVELOPMENT: {len(gt['development_periods'])}" not in output:
        passed = False
        errors.append(f"Expected {len(gt['development_periods'])} development periods")
    
    return {
        "passed": passed,
        "errors": errors if errors else None,
        "output": output
    }


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 2 output."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ldfs_weighted' in dir(), "Variable 'ldfs_weighted' not found"

if hasattr(ldfs_weighted, 'values'):
    ldfs = ldfs_weighted.values[0, 0, 0, :]
elif hasattr(ldfs_weighted, 'ldf_'):
    ldfs = ldfs_weighted.ldf_.values[0, 0, 0, :]
else:
    ldfs = ldfs_weighted

print("LDFS:", ",".join([f"{x:.6f}" for x in ldfs]))
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
    gt_ldfs = ground_truth["step_2"]["ldfs"]
    
    if "LDFS:" in output:
        ldfs_str = output.split("LDFS:")[1].strip()
        actual_ldfs = [float(x) for x in ldfs_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_ldfs, gt_ldfs)):
            if not np.isclose(actual, expected, atol=0.001):
                passed = False
                errors.append(f"LDF {i}: expected {expected:.6f}, got {actual:.6f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "ldfs": actual_ldfs
        }
    
    return {"passed": False, "error": "Could not parse LDFs from output"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 3 output."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ldfs_simple' in dir(), "Variable 'ldfs_simple' not found"

if hasattr(ldfs_simple, 'values'):
    ldfs = ldfs_simple.values[0, 0, 0, :]
elif hasattr(ldfs_simple, 'ldf_'):
    ldfs = ldfs_simple.ldf_.values[0, 0, 0, :]
else:
    ldfs = ldfs_simple

print("LDFS:", ",".join([f"{x:.6f}" for x in ldfs]))
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
    gt_ldfs = ground_truth["step_3"]["ldfs"]
    
    if "LDFS:" in output:
        ldfs_str = output.split("LDFS:")[1].strip()
        actual_ldfs = [float(x) for x in ldfs_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_ldfs, gt_ldfs)):
            if not np.isclose(actual, expected, atol=0.001):
                passed = False
                errors.append(f"LDF {i}: expected {expected:.6f}, got {actual:.6f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "ldfs": actual_ldfs
        }
    
    return {"passed": False, "error": "Could not parse LDFs from output"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 4 output."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'cdfs' in dir(), "Variable 'cdfs' not found"
assert 'ldfs_with_tail' in dir(), "Variable 'ldfs_with_tail' not found"

print("CDFS:", ",".join([f"{x:.6f}" for x in cdfs]))
print("LDFS_WITH_TAIL:", ",".join([f"{x:.6f}" for x in ldfs_with_tail]))
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
    gt_cdfs = ground_truth["step_4"]["cdfs"]
    
    if "CDFS:" in output:
        cdfs_str = output.split("CDFS:")[1].split("\n")[0].strip()
        actual_cdfs = [float(x) for x in cdfs_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_cdfs, gt_cdfs)):
            if not np.isclose(actual, expected, atol=0.001):
                passed = False
                errors.append(f"CDF {i}: expected {expected:.6f}, got {actual:.6f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "cdfs": actual_cdfs
        }
    
    return {"passed": False, "error": "Could not parse CDFs from output"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 5 output."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_ultimate' in dir(), "Variable 'total_ultimate' not found"

print(f"TOTAL_ULTIMATE: {total_ultimate:.2f}")
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
    gt_total = ground_truth["step_5"]["total_ultimate"]
    
    if "TOTAL_ULTIMATE:" in output:
        total_str = output.split("TOTAL_ULTIMATE:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:.2f}, got {actual_total:.2f}",
            "total_ultimate": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total ultimate from output"}


def validate_step_6(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 6 output."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_ibnr' in dir(), "Variable 'total_ibnr' not found"

print(f"TOTAL_IBNR: {total_ibnr:.2f}")
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
    gt_total = ground_truth["step_6"]["total_ibnr"]
    
    if "TOTAL_IBNR:" in output:
        total_str = output.split("TOTAL_IBNR:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:.2f}, got {actual_total:.2f}",
            "total_ibnr": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total IBNR from output"}

