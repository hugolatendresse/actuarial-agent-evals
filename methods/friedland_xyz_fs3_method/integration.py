import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


def generate_integration_prompt() -> str:
    prompt = []
    prompt.append("Complete Frequency-Severity Method #3 Analysis with Disposal Rates")
    prompt.append("")
    prompt.append("CRITICAL WORKSPACE RULES:")
    prompt.append("1. Work ONLY in THIS directory - the integration_solution.py file is already here")
    prompt.append("2. Use ONLY the CSV data files provided (absolute paths are in the starter code)")
    prompt.append("3. Do NOT read: methods/, test_framework/, sample_solution.py, step_*_starter_code.py,")
    prompt.append("   ground_truth.json, or ide_results/ - these are test infrastructure and answer keys")
    prompt.append("")
    prompt.append("Calculate ultimate claims by accident year using the 3rd frequency-severity method with disposal rates.")
    prompt.append("Work with accident years 2001-2008 only.")
    prompt.append("")
    prompt.append("KEY ASSUMPTIONS TO USE:")
    prompt.append("- Develop reported count to ultimate using latest 4 volume weighted average, tail 1.00")
    prompt.append("- Select disposal rates using latest 2 simple average, tail 1.00")
    prompt.append("- Severity trend: 5% per year")
    prompt.append("- Tort reform changes effective 1/1/2006 have reduced expected losses by 10.7% in accident year 2006, and by 33% in accident years 2007 and later, compared to 2005 and earlier years")
    prompt.append("- Select adjusted severities for ages 12-60 using latest 2 simple average")
    prompt.append("- Calculate tail severities for ages 72+ and 84+.")
    prompt.append("")
    prompt.append("Store the final result:")
    prompt.append("- total_ultimates_by_ay: array of total ultimate amounts by accident year (in thousands)")
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

assert 'total_ultimates_by_ay' in dir() or 'ultimates_by_ay' in dir(), "Variable 'total_ultimates_by_ay' not found"

if 'total_ultimates_by_ay' in dir():
    ultimates = total_ultimates_by_ay
elif 'ultimates_by_ay' in dir():
    ultimates = ultimates_by_ay

for i, val in enumerate(ultimates):
    print(f"ULT_{{2001+i}}: {{val:.2f}}")
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
        ultimates = []
        for line in output.split('\n'):
            if line.startswith('ULT_'):
                val = float(line.split(':')[1].strip())
                ultimates.append(val)
        
        if len(ultimates) == 0:
            return {
                "passed": False,
                "error": "Could not parse total_ultimates_by_ay from output",
                "stdout": output
            }
        
        gt_ultimates = ground_truth["step_10"]["total_ultimates_by_ay"]
        
        if len(ultimates) != len(gt_ultimates):
            return {
                "passed": False,
                "error": f"Expected {len(gt_ultimates)} ultimate values, got {len(ultimates)}",
                "ultimates": ultimates
            }
        
        passed = all(np.isclose(a, b, rtol=0.01, atol=50) for a, b in zip(ultimates, gt_ultimates))
        
        errors = []
        if not passed:
            for i, (actual, expected) in enumerate(zip(ultimates, gt_ultimates)):
                if not np.isclose(actual, expected, rtol=0.01, atol=50):
                    errors.append(f"AY {2001+i}: expected {expected:,.0f}, got {actual:,.0f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "total_ultimates_by_ay": ultimates,
            "expected_ultimates": gt_ultimates
        }
        
    except Exception as e:
        return {
            "passed": False,
            "error": f"Validation error: {e}",
            "stdout": output
        }

