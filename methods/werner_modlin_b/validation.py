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
assert 'state_ultimate_losses' in dir(), "Variable 'state_ultimate_losses' not found"

for i, val in enumerate(state_ultimate_losses):
    print(f"VALUE_{i}: {val:.2f}")
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
    gt_values = ground_truth["step_1"]["state_ultimate_losses"]
    
    try:
        actual_values = []
        for i in range(len(gt_values)):
            line = [l for l in output.split('\n') if f"VALUE_{i}:" in l][0]
            actual_values.append(float(line.split(':')[1].strip()))
        
        passed = all(np.isclose(actual_values[i], gt_values[i], rtol=0.001) for i in range(len(gt_values)))
        
        return {
            "passed": passed,
            "error": None if passed else f"Values don't match ground truth",
            "actual": actual_values,
            "expected": gt_values
        }
    except Exception as e:
        return {"passed": False, "error": f"Parse error: {e}"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'current_loss_trend_annual' in dir(), "Variable 'current_loss_trend_annual' not found"
assert 'projected_loss_trend_annual' in dir(), "Variable 'projected_loss_trend_annual' not found"

print(f"CURRENT_LOSS_TREND: {current_loss_trend_annual:.6f}")
print(f"PROJECTED_LOSS_TREND: {projected_loss_trend_annual:.6f}")
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
    gt_current = ground_truth["step_2"]["current_loss_trend_annual"]
    gt_projected = ground_truth["step_2"]["projected_loss_trend_annual"]
    
    try:
        if "CURRENT_LOSS_TREND:" in output and "PROJECTED_LOSS_TREND:" in output:
            actual_current = float(output.split("CURRENT_LOSS_TREND:")[1].split("\n")[0].strip())
            actual_projected = float(output.split("PROJECTED_LOSS_TREND:")[1].strip())
            
            passed = (np.isclose(actual_current, gt_current, atol=0.001) and 
                     np.isclose(actual_projected, gt_projected, atol=0.001))
            
            return {
                "passed": passed,
                "error": None if passed else f"Expected current: {gt_current:.6f}, got {actual_current:.6f}; Expected projected: {gt_projected:.6f}, got {actual_projected:.6f}",
                "actual": {"current": actual_current, "projected": actual_projected},
                "expected": {"current": gt_current, "projected": gt_projected}
            }
        
        return {"passed": False, "error": "Could not parse trends from output"}
    except Exception as e:
        return {"passed": False, "error": f"Parse error: {e}"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_loss_trend_factors' in dir(), "Variable 'total_loss_trend_factors' not found"

for i, val in enumerate(total_loss_trend_factors):
    print(f"VALUE_{i}: {val:.6f}")
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
    gt_values = ground_truth["step_3"]["total_loss_trend_factors"]
    
    try:
        actual_values = []
        for i in range(len(gt_values)):
            line = [l for l in output.split('\n') if f"VALUE_{i}:" in l][0]
            actual_values.append(float(line.split(':')[1].strip()))
        
        passed = all(np.isclose(actual_values[i], gt_values[i], atol=0.0001) for i in range(len(gt_values)))
        
        return {
            "passed": passed,
            "error": None if passed else f"Values don't match ground truth",
            "actual": actual_values,
            "expected": gt_values
        }
    except Exception as e:
        return {"passed": False, "error": f"Parse error: {e}"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'selected_projected_non_cat_pure_premium' in dir(), "Variable 'selected_projected_non_cat_pure_premium' not found"

print(f"SELECTED_PROJECTED_NON_CAT_PURE_PREMIUM: {selected_projected_non_cat_pure_premium:.6f}")
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
    gt_value = ground_truth["step_4"]["selected_projected_non_cat_pure_premium"]
    
    if "SELECTED_PROJECTED_NON_CAT_PURE_PREMIUM:" in output:
        actual_value = float(output.split("SELECTED_PROJECTED_NON_CAT_PURE_PREMIUM:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.5f}, got {actual_value:.5f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse selected projected non-CAT pure premium from output"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'credibility_weighted_non_cat_pure_premium' in dir(), "Variable 'credibility_weighted_non_cat_pure_premium' not found"

print(f"CREDIBILITY_WEIGHTED_NON_CAT_PURE_PREMIUM: {credibility_weighted_non_cat_pure_premium:.6f}")
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
    gt_value = ground_truth["step_5"]["credibility_weighted_non_cat_pure_premium"]
    
    if "CREDIBILITY_WEIGHTED_NON_CAT_PURE_PREMIUM:" in output:
        actual_value = float(output.split("CREDIBILITY_WEIGHTED_NON_CAT_PURE_PREMIUM:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.4f}, got {actual_value:.4f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse credibility-weighted non-CAT pure premium from output"}


def validate_step_6(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'vplr' in dir(), "Variable 'vplr' not found"

print(f"VPLR: {vplr:.6f}")
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
    gt_value = ground_truth["step_6"]["vplr"]
    
    if "VPLR:" in output:
        actual_value = float(output.split("VPLR:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.3f}, got {actual_value:.3f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse VPLR from output"}


def validate_step_7(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_indicated_pure_premium' in dir(), "Variable 'total_indicated_pure_premium' not found"

print(f"TOTAL_INDICATED_PURE_PREMIUM: {total_indicated_pure_premium:.6f}")
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
    gt_value = ground_truth["step_7"]["total_indicated_pure_premium"]
    
    if "TOTAL_INDICATED_PURE_PREMIUM:" in output:
        actual_value = float(output.split("TOTAL_INDICATED_PURE_PREMIUM:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.01)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.2f}, got {actual_value:.2f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse total indicated pure premium from output"}

