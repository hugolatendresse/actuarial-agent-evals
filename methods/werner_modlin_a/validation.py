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
assert 'step_1_earned_premium_crl' in dir(), "Variable 'step_1_earned_premium_crl' not found"

for i, val in enumerate(step_1_earned_premium_crl):
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
    gt_values = ground_truth["step_1"]["earned_premium_crl"]
    
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
assert 'step_2_premium_trend' in dir(), "Variable 'step_2_premium_trend' not found"

print(f"PREMIUM_TREND: {step_2_premium_trend:.6f}")
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
    gt_value = ground_truth["step_2"]["premium_trend_annual"]
    
    if "PREMIUM_TREND:" in output:
        actual_value = float(output.split("PREMIUM_TREND:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.4f}, got {actual_value:.4f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse premium trend from output"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_3_total_trend_factors' in dir(), "Variable 'step_3_total_trend_factors' not found"

for i, val in enumerate(step_3_total_trend_factors):
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
    gt_values = ground_truth["step_3"]["total_trend_factors"]
    
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
assert 'step_4_projected_earned_premium' in dir(), "Variable 'step_4_projected_earned_premium' not found"

for i, val in enumerate(step_4_projected_earned_premium):
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
    gt_values = ground_truth["step_4"]["projected_earned_premium"]
    
    try:
        actual_values = []
        for i in range(len(gt_values)):
            line = [l for l in output.split('\n') if f"VALUE_{i}:" in l][0]
            actual_values.append(float(line.split(':')[1].strip()))
        
        passed = all(abs(actual_values[i] - gt_values[i]) < 200 for i in range(len(gt_values)))
        
        return {
            "passed": passed,
            "error": None if passed else f"Values don't match ground truth",
            "actual": actual_values,
            "expected": gt_values
        }
    except Exception as e:
        return {"passed": False, "error": f"Parse error: {e}"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_5_ultimate_losses' in dir(), "Variable 'step_5_ultimate_losses' not found"

ay_start_idx = 2
for i in range(5):
    val = step_5_ultimate_losses[ay_start_idx + i]
    print(f"VALUE_{i}: {val:.4f}")
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
    gt_values = ground_truth["step_5"]["ultimate_losses"]
    
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


def validate_step_6(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_6_current_loss_trend' in dir(), "Variable 'step_6_current_loss_trend' not found"

print(f"CURRENT_LOSS_TREND: {step_6_current_loss_trend:.6f}")
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
    gt_value = ground_truth["step_6"]["current_loss_trend"]
    
    if "CURRENT_LOSS_TREND:" in output:
        actual_value = float(output.split("CURRENT_LOSS_TREND:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.4f}, got {actual_value:.4f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse current loss trend from output"}


def validate_step_7(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_7_projected_loss_trend' in dir(), "Variable 'step_7_projected_loss_trend' not found"

print(f"PROJECTED_LOSS_TREND: {step_7_projected_loss_trend:.6f}")
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
    gt_value = ground_truth["step_7"]["projected_loss_trend"]
    
    if "PROJECTED_LOSS_TREND:" in output:
        actual_value = float(output.split("PROJECTED_LOSS_TREND:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.4f}, got {actual_value:.4f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse projected loss trend from output"}


def validate_step_8(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_8_total_loss_trend_factors' in dir(), "Variable 'step_8_total_loss_trend_factors' not found"

for i, val in enumerate(step_8_total_loss_trend_factors):
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
    gt_values = ground_truth["step_8"]["total_loss_trend_factors"]
    
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


def validate_step_9(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_9_projected_loss_lae_ratio' in dir(), "Variable 'step_9_projected_loss_lae_ratio' not found"

print(f"PROJECTED_LOSS_LAE_RATIO: {step_9_projected_loss_lae_ratio:.6f}")
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
    gt_value = ground_truth["step_9"]["projected_loss_lae_ratio"]
    
    if "PROJECTED_LOSS_LAE_RATIO:" in output:
        actual_value = float(output.split("PROJECTED_LOSS_LAE_RATIO:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse projected loss LAE ratio from output"}


def validate_step_10(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_10_vplr' in dir(), "Variable 'step_10_vplr' not found"

print(f"VPLR: {step_10_vplr:.6f}")
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
    gt_value = ground_truth["step_10"]["vplr"]
    
    if "VPLR:" in output:
        actual_value = float(output.split("VPLR:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse VPLR from output"}


def validate_step_11(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_11_indicated_rate_change' in dir(), "Variable 'step_11_indicated_rate_change' not found"

print(f"INDICATED_RATE_CHANGE: {step_11_indicated_rate_change:.6f}")
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
    gt_value = ground_truth["step_11"]["indicated_rate_change"]
    
    if "INDICATED_RATE_CHANGE:" in output:
        actual_value = float(output.split("INDICATED_RATE_CHANGE:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse indicated rate change from output"}


def validate_step_12(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_12_credibility' in dir(), "Variable 'step_12_credibility' not found"

print(f"CREDIBILITY: {step_12_credibility:.6f}")
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
    gt_value = ground_truth["step_12"]["credibility"]
    
    if "CREDIBILITY:" in output:
        actual_value = float(output.split("CREDIBILITY:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse credibility from output"}


def validate_step_13(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_13_trended_present_rates' in dir(), "Variable 'step_13_trended_present_rates' not found"

print(f"TRENDED_PRESENT_RATES: {step_13_trended_present_rates:.6f}")
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
    gt_value = ground_truth["step_13"]["trended_present_rates"]
    
    if "TRENDED_PRESENT_RATES:" in output:
        actual_value = float(output.split("TRENDED_PRESENT_RATES:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse trended present rates from output"}


def validate_step_14(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'step_14_credibility_weighted_rate_change' in dir(), "Variable 'step_14_credibility_weighted_rate_change' not found"

print(f"CREDIBILITY_WEIGHTED_RATE_CHANGE: {step_14_credibility_weighted_rate_change:.6f}")
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
    gt_value = ground_truth["step_14"]["credibility_weighted_rate_change"]
    
    if "CREDIBILITY_WEIGHTED_RATE_CHANGE:" in output:
        actual_value = float(output.split("CREDIBILITY_WEIGHTED_RATE_CHANGE:")[1].strip())
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_value:.6f}, got {actual_value:.6f}",
            "actual": actual_value,
            "expected": gt_value
        }
    
    return {"passed": False, "error": "Could not parse credibility weighted rate change from output"}

