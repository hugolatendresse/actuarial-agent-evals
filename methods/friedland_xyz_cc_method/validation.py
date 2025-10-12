import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


SOLUTION_FILENAME = "step_solution.py"


def validate_step_1(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 1: Current level earned premium."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'current_level_earned_premium' in dir(), "Variable 'current_level_earned_premium' not found"

if hasattr(current_level_earned_premium, 'values'):
    clep_values = current_level_earned_premium.values
else:
    clep_values = current_level_earned_premium

print("CLEP:", ",".join([f"{x:.0f}" for x in clep_values]))
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
    gt_clep = ground_truth["step_1"]["current_level_earned_premium"]
    
    if "CLEP:" in output:
        clep_str = output.split("CLEP:")[1].strip()
        actual_clep = [float(x) for x in clep_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_clep, gt_clep)):
            if not np.isclose(actual, expected, rtol=0.01):
                passed = False
                errors.append(f"CLEP {i}: expected {expected:,.0f}, got {actual:,.0f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "clep": actual_clep
        }
    
    return {"passed": False, "error": "Could not parse CLEP from output"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 2: Tort reform factors."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'tort_reform_factors' in dir(), "Variable 'tort_reform_factors' not found"

if hasattr(tort_reform_factors, 'values'):
    factors = tort_reform_factors.values
else:
    factors = tort_reform_factors

print("TORT_FACTORS:", ",".join([f"{x:.3f}" for x in factors]))
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
    gt_factors = ground_truth["step_2"]["tort_reform_factors"]
    
    if "TORT_FACTORS:" in output:
        factors_str = output.split("TORT_FACTORS:")[1].strip()
        actual_factors = [float(x) for x in factors_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_factors, gt_factors)):
            if not np.isclose(actual, expected, atol=0.001):
                passed = False
                errors.append(f"Factor {i}: expected {expected:.3f}, got {actual:.3f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "tort_factors": actual_factors
        }
    
    return {"passed": False, "error": "Could not parse tort factors from output"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 3: Adjusted reported claims."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'adjusted_reported_claims' in dir(), "Variable 'adjusted_reported_claims' not found"

if hasattr(adjusted_reported_claims, 'values'):
    claims = adjusted_reported_claims.values
else:
    claims = adjusted_reported_claims

print("ADJ_CLAIMS:", ",".join([f"{x:.0f}" for x in claims]))
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
    gt_claims = ground_truth["step_3"]["adjusted_reported_claims"]
    
    if "ADJ_CLAIMS:" in output:
        claims_str = output.split("ADJ_CLAIMS:")[1].strip()
        actual_claims = [float(x) for x in claims_str.split(",")]
        
        passed = True
        errors = []
        for i, (actual, expected) in enumerate(zip(actual_claims, gt_claims)):
            if not np.isclose(actual, expected, rtol=0.01):
                passed = False
                errors.append(f"Adjusted claim {i}: expected {expected:,.0f}, got {actual:,.0f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "adjusted_claims": actual_claims
        }
    
    return {"passed": False, "error": "Could not parse adjusted claims from output"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 4: Cape Cod ultimates."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_cc_ultimate' in dir(), "Variable 'total_cc_ultimate' not found"

print(f"TOTAL_CC_ULTIMATE: {total_cc_ultimate:.2f}")
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
    gt_total = ground_truth["step_4"]["total_cc_ultimate"]
    
    if "TOTAL_CC_ULTIMATE:" in output:
        total_str = output.split("TOTAL_CC_ULTIMATE:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "total_cc_ultimate": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total_cc_ultimate from output"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 5: Cape Cod IBNR."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_cc_ibnr' in dir(), "Variable 'total_cc_ibnr' not found"

print(f"TOTAL_CC_IBNR: {total_cc_ibnr:.2f}")
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
    gt_total = ground_truth["step_5"]["total_cc_ibnr"]
    
    if "TOTAL_CC_IBNR:" in output:
        total_str = output.split("TOTAL_CC_IBNR:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "total_cc_ibnr": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total_cc_ibnr from output"}

