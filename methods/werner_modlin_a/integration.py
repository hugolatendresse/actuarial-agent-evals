import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


def generate_integration_prompt() -> str:
    prompt = []
    prompt.append("Complete Werner-Modlin Loss Ratio Ratemaking Analysis")
    prompt.append("")
    prompt.append("CRITICAL WORKSPACE RULES:")
    prompt.append("1. Work ONLY in THIS directory - the integration_solution.py file is already here")
    prompt.append("2. Use ONLY the CSV data files provided (absolute paths are in the starter code)")
    prompt.append("3. Do NOT read: methods/, test_framework/, sample_solution.py, step_*_starter_code.py,")
    prompt.append("   ground_truth.json, or ide_results/ - these are test infrastructure and answer keys")
    prompt.append("")
    prompt.append("Using the provided data files, perform a complete loss ratio rate indication analysis:")
    prompt.append("")
    prompt.append("Premium assumptions:")
    prompt.append("- Use an 8-point exponential trend on rolling 4-quarter average premiums per exposure")
    prompt.append("")
    prompt.append("Loss assumptions:")
    prompt.append("- Develop using the chainladder method with all-years straight average")
    prompt.append("  excluding high and low, with a 1.0 tail factor at age 63")
    prompt.append("- Calculate current loss trend using 8-point exponential trends for frequency and severity")
    prompt.append("- Calculate projected loss trend using 4-point exponential trends for frequency and severity")
    prompt.append("- Use a ULAE factor of 1.143")
    prompt.append("")
    prompt.append("Other assumptions:")
    prompt.append("  * Variable expense provision: 16.9956%")
    prompt.append("  * Underwriting profit provision: 5%")
    prompt.append("  * Fixed expense provision: 11.2867%")
    prompt.append("- Credibility weight the indication with the trended present rates indication")
    prompt.append("  * Total claims in historical period: 700")
    prompt.append("  * Claims for full credibility: 1082")
    prompt.append("  * Last rate change effective: 1/1/2016")
    prompt.append("  * Latest indicated rate change: 13.2%")
    prompt.append("  * Last rate change taken: 5%")
    prompt.append("")
    prompt.append("Policy details:")
    prompt.append("- Policy term: 6 months")
    prompt.append("- Rates will be in effect for 12 months starting 1/1/2017")
    prompt.append("- Calendar years: 2011-2015")
    prompt.append("- Accident years: 2011-2015")
    prompt.append("")
    prompt.append("Store the final result in variable:")
    prompt.append("- credibility_weighted_rate_change: final credibility-weighted rate change")
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

assert 'credibility_weighted_rate_change' in dir(), "Variable 'credibility_weighted_rate_change' not found"

print(f"CREDIBILITY_WEIGHTED_RATE_CHANGE: {{credibility_weighted_rate_change:.6f}}")
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
        if 'CREDIBILITY_WEIGHTED_RATE_CHANGE:' in output:
            actual_value = float(output.split('CREDIBILITY_WEIGHTED_RATE_CHANGE:')[1].strip())
        else:
            return {
                "passed": False,
                "error": "Could not parse credibility_weighted_rate_change from output",
                "stdout": output
            }
        
        gt_value = ground_truth["step_14"]["credibility_weighted_rate_change"]
        
        passed = np.isclose(actual_value, gt_value, atol=0.001)
        
        errors = []
        if not passed:
            errors.append(f"Credibility-weighted rate change: expected {gt_value:.6f}, got {actual_value:.6f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "credibility_weighted_rate_change": actual_value,
            "expected": gt_value
        }
        
    except Exception as e:
        return {
            "passed": False,
            "error": f"Validation error: {e}",
            "stdout": output
        }

