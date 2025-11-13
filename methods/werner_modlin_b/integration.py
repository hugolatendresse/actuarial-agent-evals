import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


def generate_integration_prompt() -> str:
    prompt = []
    prompt.append("Complete Werner-Modlin Loss Cost Ratemaking Analysis - Method B")
    prompt.append("")
    prompt.append("CRITICAL WORKSPACE RULES:")
    prompt.append("1. Work ONLY in THIS directory - the integration_solution.py file is already here")
    prompt.append("2. Use ONLY the CSV data files provided (absolute paths are in the starter code)")
    prompt.append("3. Do NOT read: methods/, test_framework/, sample_solution.py, step_*_starter_code.py,")
    prompt.append("   ground_truth.json, or ide_results/ - these are test infrastructure and answer keys")
    prompt.append("")
    prompt.append("Using the provided data files, perform a complete pure premium rate indication analysis:")
    prompt.append("")
    prompt.append("Data files:")
    prompt.append("- State earned exposures and reported loss+ALAE")
    prompt.append("- Regional quarterly pure premium data")
    prompt.append("- Countrywide reported loss+ALAE triangle")
    prompt.append("")
    prompt.append("Loss assumptions:")
    prompt.append("- Develop state losses using countrywide LDFs from chainladder method")
    prompt.append("  with an all-years simple average, 1% tail factor at age 63")
    prompt.append("- Calculate current loss trend using 8-point exponential trend")
    prompt.append("- Calculate projected loss trend using 4-point exponential trend")
    prompt.append("- Use a ULAE factor of 1.011812")
    prompt.append("")
    prompt.append("Credibility:")
    prompt.append("- Total reported claims (5-year): 683")
    prompt.append("- Claims for full credibility: 1082")
    prompt.append("- Regional non-CAT pure premium: $585.75")
    prompt.append("")
    prompt.append("Other loading amounts:")
    prompt.append("- Total CAT pure premium: $103.85")
    prompt.append("- Projected net reinsurance cost per exposure: $15.68")
    prompt.append("- Projected fixed expense per exposure: $77.74")
    prompt.append("- Variable expense provision: 13.8%")
    prompt.append("- Profit and contingency provision: 5%")
    prompt.append("")
    prompt.append("Policy details:")
    prompt.append("- Policy term: 12 months")
    prompt.append("- Rates will be in effect for 12 months starting 1/1/2017")
    prompt.append("")
    prompt.append("Store the final result in variable:")
    prompt.append("- total_indicated_pure_premium: final total indicated pure premium")
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

assert 'total_indicated_pure_premium' in dir(), "Variable 'total_indicated_pure_premium' not found"

print(f"TOTAL_INDICATED_PURE_PREMIUM: {{total_indicated_pure_premium:.6f}}")
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
        if 'TOTAL_INDICATED_PURE_PREMIUM:' in output:
            actual_value = float(output.split('TOTAL_INDICATED_PURE_PREMIUM:')[1].strip())
        else:
            return {
                "passed": False,
                "error": "Could not parse total_indicated_pure_premium from output",
                "stdout": output
            }
        
        gt_value = ground_truth["step_7"]["total_indicated_pure_premium"]
        
        passed = np.isclose(actual_value, gt_value, atol=0.01)
        
        errors = []
        if not passed:
            errors.append(f"Total indicated pure premium: expected {gt_value:.2f}, got {actual_value:.2f}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "total_indicated_pure_premium": actual_value,
            "expected": gt_value
        }
        
    except Exception as e:
        return {
            "passed": False,
            "error": f"Validation error: {e}",
            "stdout": output
        }

