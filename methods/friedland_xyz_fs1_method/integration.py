import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


def generate_integration_prompt() -> str:
    prompt = []
    prompt.append("Complete Frequency-Severity Method Analysis")
    prompt.append("")
    prompt.append("CRITICAL WORKSPACE RULES:")
    prompt.append("1. Work ONLY in THIS directory - the integration_solution.py file is already here")
    prompt.append("2. Use ONLY the CSV data files provided (absolute paths are in the starter code)")
    prompt.append("3. Do NOT read: methods/, test_framework/, sample_solution.py, step_*_starter_code.py,")
    prompt.append("   ground_truth.json, or ide_results/ - these are test infrastructure and answer keys")
    prompt.append("")
    prompt.append("Calculate ultimate claims and IBNR using the frequency-severity method that develops")
    prompt.append("frequency and severity to ultimate separately. Develop the CWP and reported count triangles")
    prompt.append("to ultimate using latest 4 volume weighted average with 1.00 tail, then take the average")
    prompt.append("of the two count ultimates. Develop severity (claims/counts) using latest 5 simple average")
    prompt.append("with 1.01 tail.")
    prompt.append("")
    prompt.append("Store these final results:")
    prompt.append("- total_ultimate: total ultimate amount")
    prompt.append("- total_ibnr: total IBNR amount")
    prompt.append("")
    prompt.append("TESTING WORKFLOW:")
    prompt.append("1. Edit integration_solution.py (already exists in THIS directory)")
    prompt.append("2. Write code below the marker line")
    prompt.append("3. Test by running: python integration_solution.py")
    prompt.append("4. Debug and fix any errors")
    prompt.append("5. ONLY when working perfectly, add this exact line at the end:")
    prompt.append("   ## SOLUTION COMPLETE - TESTED AND WORKING")
    prompt.append("")
    prompt.append("WARNING: The system evaluates immediately when it sees the completion marker!")
    
    return "\n".join(prompt)


def validate_integration(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    project_root = Path.cwd()
    
    validation_code = f"""
import sys
import os

os.chdir(r'{project_root}')
sys.path.insert(0, '.')

with open(r'{workspace_dir / "integration_solution.py"}', 'r') as f:
    solution_code = f.read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', '')

exec(solution_code)

import numpy as np

assert 'total_ultimate' in dir(), "Variable 'total_ultimate' not found"
assert 'total_ibnr' in dir(), "Variable 'total_ibnr' not found"

print(f"TOTAL_ULTIMATE: {{total_ultimate:.2f}}")
print(f"TOTAL_IBNR: {{total_ibnr:.2f}}")
"""
    
    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(validation_code)
    
    venv_python = Path("venv/bin/python")
    python_cmd = str(venv_python.absolute()) if venv_python.exists() else "python"
    
    result = subprocess.run(
        [python_cmd, "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        return {
            "passed": False,
            "error": f"Execution error: {result.stderr}",
            "stdout": result.stdout
        }
    
    output = result.stdout
    
    try:
        total_ultimate = None
        total_ibnr = None
        
        for line in output.split('\n'):
            if 'TOTAL_ULTIMATE:' in line:
                total_ultimate = float(line.split(':')[1].strip())
            elif 'TOTAL_IBNR:' in line:
                total_ibnr = float(line.split(':')[1].strip())
        
        if total_ultimate is None or total_ibnr is None:
            return {
                "passed": False,
                "error": "Could not parse total_ultimate or total_ibnr from output",
                "stdout": output
            }
        
        gt_ultimate = ground_truth["step_5"]["total_ultimate"]
        gt_ibnr = ground_truth["step_5"]["total_ibnr"]
        
        ultimate_match = np.isclose(total_ultimate, gt_ultimate, rtol=0.001)
        ibnr_match = np.isclose(total_ibnr, gt_ibnr, rtol=0.001)
        
        errors = []
        if not ultimate_match:
            errors.append(f"Total ultimate: expected {gt_ultimate:,.2f}, got {total_ultimate:,.2f}")
        if not ibnr_match:
            errors.append(f"Total IBNR: expected {gt_ibnr:,.2f}, got {total_ibnr:,.2f}")
        
        passed = ultimate_match and ibnr_match
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "total_ultimate": total_ultimate,
            "total_ibnr": total_ibnr,
            "expected_ultimate": gt_ultimate,
            "expected_ibnr": gt_ibnr
        }
        
    except Exception as e:
        return {
            "passed": False,
            "error": f"Validation error: {e}",
            "stdout": output
        }

