"""
Actuarial Test Harness for Sequential Method Testing

This harness tests actuarial methods step-by-step, building cumulative code
and validating each intermediate result.

Usage:
  python actuarial_test_harness.py --method friedland_xyz_dev_method --ide cursor --mode auto
  python actuarial_test_harness.py --method friedland_xyz_dev_method --ide cursor --mode manual
  python actuarial_test_harness.py --method friedland_xyz_dev_method --ide cursor --step step_2
"""

import json
import subprocess
import os
import shutil
import time
import argparse
import numpy as np
import pandas as pd
import signal
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pyperclip

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


RESULTS_DIR = "actuarial_results"
STEP_SOLUTION_FILENAME = "step_solution.py"


class StepSolutionHandler(FileSystemEventHandler):
    """Handler that waits for step solution file to be created and marked complete."""
    
    def __init__(self, filename_to_watch, workspace_dir):
        self.filename_to_watch = filename_to_watch
        self.workspace_dir = workspace_dir
        self.file_path = None
        self.file_ready = False
    
    def _has_completion_marker(self, file_path):
        """Check if the solution has the completion marker."""
        completion_marker = "## STEP COMPLETE - TESTED AND WORKING"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return completion_marker in content
        except (IOError, UnicodeDecodeError):
            return False
    
    def on_created(self, event):
        """Called when a file is created."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"\nDetected '{self.filename_to_watch}' created.")
            self.file_path = event.src_path
            
            if self._has_completion_marker(event.src_path):
                print("'## STEP COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for '## STEP COMPLETE - TESTED AND WORKING' marker...")
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            
            if self._has_completion_marker(event.src_path):
                print("'## STEP COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for '## STEP COMPLETE - TESTED AND WORKING' marker...")


class ActuarialTestHarness:
    """Test harness for sequential actuarial method testing."""
    
    def __init__(self, method_name: str, mode: str = 'manual'):
        self.method_name = method_name
        self.mode = mode
        self.method_dir = Path("test_data") / method_name
        self.results_dir = Path(RESULTS_DIR) / method_name
        self.ground_truth = self._load_ground_truth()
        self.steps = self._define_steps()
        self.first_question = True
        
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\nInterruption detected. Exiting...")
        sys.exit(0)
    
    def _load_ground_truth(self) -> Dict[str, Any]:
        """Load ground truth data for the method."""
        ground_truth_path = self.method_dir / "ground_truth.json"
        with open(ground_truth_path, 'r') as f:
            return json.load(f)
    
    def _define_steps(self) -> List[Dict[str, Any]]:
        """Define the steps for the Friedland XYZ development method."""
        if self.method_name == "friedland_xyz_dev_method":
            return [
                {
                    "step_id": "step_1",
                    "description": "Load the triangle data and convert it to chainladder triangle",
                    "prompt_template": self._get_step_1_prompt,
                    "validation": self._validate_step_1,
                },
                {
                    "step_id": "step_2",
                    "description": "Calculate volume-weighted average LDFs using latest 3 periods",
                    "prompt_template": self._get_step_2_prompt,
                    "validation": self._validate_step_2,
                },
                {
                    "step_id": "step_3",
                    "description": "Calculate simple average LDFs using latest 5 periods",
                    "prompt_template": self._get_step_3_prompt,
                    "validation": self._validate_step_3,
                },
                {
                    "step_id": "step_4",
                    "description": "Calculate CDFs with 1.00 tail factor from age 132",
                    "prompt_template": self._get_step_4_prompt,
                    "validation": self._validate_step_4,
                },
                {
                    "step_id": "step_5",
                    "description": "Calculate ultimates using CDFs from step 4",
                    "prompt_template": self._get_step_5_prompt,
                    "validation": self._validate_step_5,
                },
                {
                    "step_id": "step_6",
                    "description": "Calculate IBNR reserves",
                    "prompt_template": self._get_step_6_prompt,
                    "validation": self._validate_step_6,
                },
            ]
        else:
            raise ValueError(f"Unknown method: {self.method_name}")
    
    def _get_data_files(self) -> List[Path]:
        """Get list of data files for the method."""
        csv_files = list(self.method_dir.glob("*.csv"))
        return csv_files
    
    def _create_base_file(self, workspace_dir: Path, previous_code: str = "") -> str:
        """Create the base Python file with data paths and previous code."""
        lines = []
        lines.append("import pandas as pd")
        lines.append("import numpy as np")
        lines.append("import chainladder as cl")
        lines.append("from pathlib import Path")
        lines.append("")
        
        # Add data file paths
        data_files = self._get_data_files()
        if data_files:
            lines.append("# Data file paths")
            for i, data_file in enumerate(sorted(data_files)):
                abs_path = data_file.resolve()
                lines.append(f"data_path_{i+1} = r'{abs_path}'")
            lines.append("")
        
        # Add previous code if any
        if previous_code:
            lines.append("# Code from previous steps")
            lines.append(previous_code)
            lines.append("")
        
        lines.append("### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###")
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_step_1_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 1."""
        prompt = []
        prompt.append("STEP 1: Load Triangle Data and Convert to Chainladder Triangle")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Load the reported claims triangle from the CSV file")
        prompt.append("2. Clean and prepare the data")
        prompt.append("3. Convert it to a chainladder Triangle object")
        prompt.append("4. The triangle should be cumulative")
        prompt.append("")
        prompt.append("Important notes:")
        prompt.append("- The CSV has development ages in months (12, 24, 36, etc.)")
        prompt.append("- Age 12 means 12 months from start of accident year (still in same calendar year)")
        prompt.append("- You need to convert ages to proper valuation dates: AY 2008 at age 12 = December 2008")
        prompt.append("- Use pd.DateOffset(months=age-1) to calculate valuation dates correctly")
        prompt.append("")
        prompt.append("Store the result in a variable called: triangle")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_2_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 2."""
        prompt = []
        prompt.append("STEP 2: Calculate Volume-Weighted Average LDFs")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Calculate volume-weighted average Link Development Factors (LDFs)")
        prompt.append("2. Use the latest 3 periods for averaging")
        prompt.append("3. Use chainladder library's Development class with average='volume' and n_periods=3")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ldfs_weighted: array of LDFs")
        prompt.append("")
        prompt.append("Expected LDFs (for validation):")
        prompt.append("1.674, 1.325, 1.147, 1.060, 1.060, 1.028, 1.005, 0.998, 0.993, 0.999")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_3_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 3."""
        prompt = []
        prompt.append("STEP 3: Calculate Simple Average LDFs")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Calculate simple (unweighted) average Link Development Factors (LDFs)")
        prompt.append("2. Use the latest 5 periods for averaging")
        prompt.append("3. Use chainladder library's Development class with average='simple' and n_periods=5")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ldfs_simple: array of LDFs")
        prompt.append("")
        prompt.append("Expected LDFs (for validation):")
        prompt.append("1.827, 1.417, 1.247, 1.124, 1.082, 1.040, 1.031, 0.997, 0.991, 0.999")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_4_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 4."""
        prompt = []
        prompt.append("STEP 4: Calculate CDFs with Tail Factor")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Take the volume-weighted LDFs from Step 2 (ldfs_weighted)")
        prompt.append("2. Append a tail factor of 1.00 representing development from age 132 to Ultimate")
        prompt.append("3. Calculate Cumulative Development Factors (CDFs) by taking cumulative product from tail to first age")
        prompt.append("")
        prompt.append("Formula: CDF at each age = product of all LDFs from that age to ultimate")
        prompt.append("Hint: Use np.cumprod() on reversed array, then reverse result")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ldfs_with_tail: LDFs including tail factor (length 11)")
        prompt.append("- cdfs: Cumulative Development Factors (length 11)")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_5_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 5."""
        prompt = []
        prompt.append("STEP 5: Calculate Ultimate Claims")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Use the CDFs from Step 4 to calculate ultimate claims for each accident year")
        prompt.append("2. Get the latest diagonal values from the triangle")
        prompt.append("3. For each accident year, multiply latest value by appropriate CDF")
        prompt.append("4. Calculate total ultimates across all years")
        prompt.append("")
        prompt.append("Formula: Ultimate = Latest Value × CDF at that development age")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ultimates: array of ultimate values by accident year")
        prompt.append("- total_ultimate: sum of all ultimates")
        prompt.append("")
        prompt.append("Expected total ultimate (validation): approximately 540,972,000")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_6_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 6."""
        prompt = []
        prompt.append("STEP 6: Calculate IBNR Reserves")
        prompt.append("")
        prompt.append("Your task:")
        prompt.append("1. Calculate IBNR (Incurred But Not Reported) reserves")
        prompt.append("2. IBNR = Ultimate - Latest for each accident year")
        prompt.append("3. Calculate total IBNR across all years")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ibnr: array of IBNR values by accident year")
        prompt.append("- total_ibnr: sum of all IBNR")
        prompt.append("")
        prompt.append("Expected total IBNR (validation): approximately 91,346,000")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _validate_step_1(self, workspace_dir: Path) -> Dict[str, Any]:
        """Validate step 1 output."""
        result = subprocess.run(
            ["python", STEP_SOLUTION_FILENAME],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"passed": False, "error": f"Execution error: {result.stderr}"}
        
        # Check that triangle was created with correct shape
        check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

# Validate triangle
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
        gt = self.ground_truth["step_1"]
        
        # Parse output
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
    
    def _validate_step_2(self, workspace_dir: Path) -> Dict[str, Any]:
        """Validate step 2 output."""
        check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ldfs_weighted' in dir(), "Variable 'ldfs_weighted' not found"

# Extract LDFs
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
        gt_ldfs = self.ground_truth["step_2"]["ldfs"]
        
        # Parse LDFs from output
        if "LDFS:" in output:
            ldfs_str = output.split("LDFS:")[1].strip()
            actual_ldfs = [float(x) for x in ldfs_str.split(",")]
            
            # Compare with tolerance
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
    
    def _validate_step_3(self, workspace_dir: Path) -> Dict[str, Any]:
        """Validate step 3 output."""
        check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## STEP COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'ldfs_simple' in dir(), "Variable 'ldfs_simple' not found"

# Extract LDFs
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
        gt_ldfs = self.ground_truth["step_3"]["ldfs"]
        
        # Parse LDFs from output
        if "LDFS:" in output:
            ldfs_str = output.split("LDFS:")[1].strip()
            actual_ldfs = [float(x) for x in ldfs_str.split(",")]
            
            # Compare with tolerance
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
    
    def _validate_step_4(self, workspace_dir: Path) -> Dict[str, Any]:
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
        gt_cdfs = self.ground_truth["step_4"]["cdfs"]
        
        # Parse CDFs from output
        if "CDFS:" in output:
            cdfs_str = output.split("CDFS:")[1].split("\n")[0].strip()
            actual_cdfs = [float(x) for x in cdfs_str.split(",")]
            
            # Compare with tolerance
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
    
    def _validate_step_5(self, workspace_dir: Path) -> Dict[str, Any]:
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
        gt_total = self.ground_truth["step_5"]["total_ultimate"]
        
        # Parse total ultimate from output
        if "TOTAL_ULTIMATE:" in output:
            total_str = output.split("TOTAL_ULTIMATE:")[1].strip()
            actual_total = float(total_str)
            
            # Compare with tolerance (0.1% tolerance)
            passed = np.isclose(actual_total, gt_total, rtol=0.001)
            
            return {
                "passed": passed,
                "error": None if passed else f"Expected {gt_total:.2f}, got {actual_total:.2f}",
                "total_ultimate": actual_total
            }
        
        return {"passed": False, "error": "Could not parse total ultimate from output"}
    
    def _validate_step_6(self, workspace_dir: Path) -> Dict[str, Any]:
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
        gt_total = self.ground_truth["step_6"]["total_ibnr"]
        
        # Parse total IBNR from output
        if "TOTAL_IBNR:" in output:
            total_str = output.split("TOTAL_IBNR:")[1].strip()
            actual_total = float(total_str)
            
            # Compare with tolerance (0.1% tolerance)
            passed = np.isclose(actual_total, gt_total, rtol=0.001)
            
            return {
                "passed": passed,
                "error": None if passed else f"Expected {gt_total:.2f}, got {actual_total:.2f}",
                "total_ibnr": actual_total
            }
        
        return {"passed": False, "error": "Could not parse total IBNR from output"}
    
    def run_step(self, step_data: Dict[str, Any], ide_name: str, previous_code: str = "") -> Dict[str, Any]:
        """Run a single step of the test."""
        step_id = step_data["step_id"]
        workspace_dir = self.results_dir / step_id
        
        # Clean and create workspace
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base file with previous code
        base_content = self._create_base_file(workspace_dir, previous_code)
        solution_path = workspace_dir / STEP_SOLUTION_FILENAME
        with open(solution_path, 'w') as f:
            f.write(base_content)
        
        # Generate prompt
        prompt = step_data["prompt_template"](step_data)
        
        # Add standard testing instructions
        full_prompt = self._build_full_prompt(step_id, step_data["description"], prompt, workspace_dir)
        
        # Copy to clipboard
        try:
            pyperclip.copy(full_prompt)
            print("Prompt copied to clipboard.")
        except Exception as e:
            print(f"Could not copy to clipboard: {e}")
            print("--- PROMPT ---")
            print(full_prompt)
            print("--------------")
        
        print("\n--- ACTION REQUIRED ---")
        print(f"Step: {step_id}")
        print(f"Workspace: {workspace_dir.absolute()}")
        print(f"1. Open the folder in '{ide_name}'")
        print(f"2. Work in file: {STEP_SOLUTION_FILENAME}")
        print(f"3. Paste and follow the instructions from clipboard")
        print(f"4. When complete, add: ## STEP COMPLETE - TESTED AND WORKING")
        print(f"\n< Waiting for {STEP_SOLUTION_FILENAME} to be marked complete... >")
        
        # Set up file watcher
        event_handler = StepSolutionHandler(STEP_SOLUTION_FILENAME, workspace_dir)
        observer = Observer()
        observer.schedule(event_handler, str(workspace_dir), recursive=False)
        observer.start()
        
        try:
            while not event_handler.file_ready:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
        
        # Validate the solution
        print("\n--- Validating Solution ---")
        validation_result = step_data["validation"](workspace_dir)
        
        if validation_result["passed"]:
            print(f"✓ {step_id} PASSED")
        else:
            print(f"✗ {step_id} FAILED")
            if "error" in validation_result:
                print(f"  Error: {validation_result['error']}")
            if "errors" in validation_result and validation_result["errors"]:
                for error in validation_result["errors"]:
                    print(f"  - {error}")
        
        # Extract code from solution file (excluding completion marker)
        with open(solution_path, 'r') as f:
            solution_code = f.read()
        
        # Remove completion marker and get code after the write line
        code_parts = solution_code.split("### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###")
        if len(code_parts) > 1:
            new_code = code_parts[1].replace("## STEP COMPLETE - TESTED AND WORKING", "").strip()
        else:
            new_code = ""
        
        return {
            "step_id": step_id,
            "passed": validation_result["passed"],
            "validation_result": validation_result,
            "new_code": new_code,
            "workspace": str(workspace_dir.absolute())
        }
    
    def _build_full_prompt(self, step_id: str, description: str, step_prompt: str, workspace_dir: Path) -> str:
        """Build complete prompt with standard testing instructions."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"{step_id.upper()}: {description}")
        lines.append("=" * 80)
        lines.append("")
        lines.append(step_prompt)
        lines.append("")
        lines.append("=" * 80)
        lines.append("MANDATORY WORKFLOW:")
        lines.append("=" * 80)
        lines.append(f"1. Work in file: {workspace_dir / STEP_SOLUTION_FILENAME}")
        lines.append("2. Write your code BELOW the marker line")
        lines.append("3. Test your code by running it: python step_solution.py")
        lines.append("4. Fix any errors and test again")
        lines.append("5. ONLY when working perfectly, add this line at the end:")
        lines.append("   ## STEP COMPLETE - TESTED AND WORKING")
        lines.append("")
        lines.append("WARNING: The system evaluates immediately when it sees the completion marker!")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def run_all_steps(self, ide_name: str, start_from: Optional[str] = None, single_step: Optional[str] = None):
        """Run all steps or specific step(s)."""
        print(f"\nActuarial Test Harness - {self.method_name}")
        print(f"IDE: {ide_name}")
        print(f"Mode: {self.mode}")
        print("=" * 80)
        
        # Determine which steps to run
        if single_step:
            steps_to_run = [s for s in self.steps if s["step_id"] == single_step]
            if not steps_to_run:
                print(f"ERROR: Step '{single_step}' not found")
                return
        elif start_from:
            start_idx = next((i for i, s in enumerate(self.steps) if s["step_id"] == start_from), None)
            if start_idx is None:
                print(f"ERROR: Step '{start_from}' not found")
                return
            steps_to_run = self.steps[start_idx:]
        else:
            steps_to_run = self.steps
        
        results = []
        cumulative_code = ""
        
        for i, step in enumerate(steps_to_run):
            print(f"\n{'=' * 80}")
            print(f"Running Step {i+1}/{len(steps_to_run)}: {step['step_id']}")
            print(f"{'=' * 80}")
            
            result = self.run_step(step, ide_name, cumulative_code)
            results.append(result)
            
            # Add this step's code to cumulative code
            if result["new_code"]:
                cumulative_code += "\n" + result["new_code"] + "\n"
            
            # Stop if step failed
            if not result["passed"]:
                print(f"\n✗ Step {step['step_id']} failed. Stopping.")
                break
        
        # Print summary
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        for result in results:
            status = "✓ PASSED" if result["passed"] else "✗ FAILED"
            print(f"{result['step_id']}: {status}")
        
        passed_count = sum(1 for r in results if r["passed"])
        print(f"\nTotal: {passed_count}/{len(results)} steps passed")
        print(f"{'=' * 80}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Actuarial Test Harness')
    parser.add_argument('--method', type=str, required=True,
                        help='Actuarial method to test (e.g., friedland_xyz_dev_method)')
    parser.add_argument('--ide', type=str, required=True,
                        help='IDE to use (e.g., cursor, continue, cline)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation')
    parser.add_argument('--start-from', type=str,
                        help='Start from specific step ID')
    parser.add_argument('--step', type=str,
                        help='Run only specific step ID')
    
    args = parser.parse_args()
    
    harness = ActuarialTestHarness(args.method, args.mode)
    harness.run_all_steps(args.ide, start_from=args.start_from, single_step=args.step)

