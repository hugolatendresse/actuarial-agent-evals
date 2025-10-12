import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


SOLUTION_FILENAME = "step_solution.py"


def validate_step_1(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 1 output: BF ultimate claims."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_bf_ultimate' in dir(), "Variable 'total_bf_ultimate' not found"

print(f"TOTAL_BF_ULTIMATE: {total_bf_ultimate:.2f}")
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
    gt_total = ground_truth["step_1"]["total_bf_ultimate"]
    
    if "TOTAL_BF_ULTIMATE:" in output:
        total_str = output.split("TOTAL_BF_ULTIMATE:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "total_bf_ultimate": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total_bf_ultimate from output"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate step 2 output: BF IBNR."""
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'total_bf_ibnr' in dir(), "Variable 'total_bf_ibnr' not found"

print(f"TOTAL_BF_IBNR: {total_bf_ibnr:.2f}")
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
    gt_total = ground_truth["step_2"]["total_bf_ibnr"]
    
    if "TOTAL_BF_IBNR:" in output:
        total_str = output.split("TOTAL_BF_IBNR:")[1].strip()
        actual_total = float(total_str)
        
        passed = np.isclose(actual_total, gt_total, rtol=0.001)
        
        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_total:,.2f}, got {actual_total:,.2f}",
            "total_bf_ibnr": actual_total
        }
    
    return {"passed": False, "error": "Could not parse total_bf_ibnr from output"}

