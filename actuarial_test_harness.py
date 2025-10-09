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
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
import pyperclip
import pyautogui

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


RESULTS_DIR = "ide_results"
STEP_SOLUTION_FILENAME = "step_solution.py"


def get_platform_keys(ide_name=None):
    """Get the correct key combinations for the current platform and IDE."""
    system = platform.system().lower()
    
    # Base keys for the platform
    if system == 'darwin':  # macOS
        base_keys = {
            'chat_activate': ['command', 'l'],
            'new_chat': ['command', 'n'],
            'paste': ['command', 'v']
        }
    else:  # Windows/Linux
        base_keys = {
            'chat_activate': ['ctrl', 'l'],
            'new_chat': ['ctrl', 'n'],
            'paste': ['ctrl', 'v']
        }
    
    # IDE-specific overrides
    if ide_name and ide_name.lower() == 'continue':
        # For Continue, we only use chat_activate (Ctrl+L), no new_chat
        base_keys['new_chat'] = None
    elif ide_name and ide_name.lower() == 'cline':
        # For Cline, use Cmd+' (or Ctrl+') to activate chat, Cmd+N for new chat
        if system == 'darwin':  # macOS
            base_keys['chat_activate'] = ['command', '\'']
        else: 
            base_keys['chat_activate'] = ['ctrl', '\'']
    
    return base_keys


def automate_ide_input(prompt_text, ide_name, is_first_question=True, delay_before=2.0, delay_between=1.0):
    """Automate the process of pasting prompt into the specified IDE.
    
    Args:
        prompt_text: The text to paste (should already be in clipboard)
        ide_name: Name of the IDE being tested (cursor, continue, etc.)
        is_first_question: Whether this is the first question (needs Cmd+L to activate)
        delay_before: Seconds to wait before starting automation
        delay_between: Seconds to wait between key presses
    """
    keys = get_platform_keys(ide_name)
    
    print(f"Automating {ide_name} input...")
    
    # Countdown
    for i in range(int(delay_before), 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1.0)
    
    try:
        # Try to activate IDE application first (macOS specific)
        system = platform.system().lower()
        if system == 'darwin':
            ide_app_name = "Cursor" if ide_name.lower() == "cursor" else ide_name.title()
            print(f"Attempting to activate {ide_app_name} application...")
            # Use AppleScript to activate the IDE
            try:
                subprocess.run(['osascript', '-e', f'tell application "{ide_app_name}" to activate'], 
                             check=False, capture_output=True)
                time.sleep(1.0)  # Give time for app to activate
            except Exception as e:
                print(f"Could not activate {ide_app_name} app: {e}")
                print(f"Please make sure {ide_app_name} is manually focused.")
        
        # Activate chat box - for Continue, always activate; for others, only on first question
        should_activate_chat = is_first_question or (ide_name and ide_name.lower() == 'continue')
        if should_activate_chat:
            print("   → Activating chat...")
            chat_keys = keys['chat_activate']
            
            # Use keyDown/keyUp with delays for reliable key combinations
            pyautogui.keyDown(chat_keys[0])
            time.sleep(0.1)  # Small delay
            pyautogui.keyDown(chat_keys[1])
            time.sleep(0.1)  # Small delay
            pyautogui.keyUp(chat_keys[1])
            time.sleep(0.1)  # Small delay
            pyautogui.keyUp(chat_keys[0])
            
            # Give time for focus to switch
            time.sleep(delay_between)
        
        # Create new chat (only for IDEs that support it)
        if keys['new_chat'] is not None:
            print("   → Creating new chat...")
            new_chat_keys = keys['new_chat']
            
            pyautogui.keyDown(new_chat_keys[0])
            time.sleep(0.1)  # Small delay
            pyautogui.keyDown(new_chat_keys[1])
            time.sleep(0.1)  # Small delay
            pyautogui.keyUp(new_chat_keys[1])
            time.sleep(0.1)  # Small delay
            pyautogui.keyUp(new_chat_keys[0])
            
            # Give time for confirmation dialog to appear if needed
            time.sleep(delay_between)
            
            # Press Enter to confirm new chat if dialog appears
            print("   → Confirming new chat...")
            pyautogui.press('enter')
            
            # Give more time for new chat to be created
            time.sleep(delay_between)
        else:
            print("   → Skipping new chat creation (not supported by this IDE)")
            time.sleep(delay_between)
        
        # Paste the prompt
        print("   → Pasting prompt...")
        paste_keys = keys['paste']
        
        pyautogui.keyDown(paste_keys[0])
        time.sleep(0.1)  # Small delay
        pyautogui.keyDown(paste_keys[1])
        time.sleep(0.1)  # Small delay
        pyautogui.keyUp(paste_keys[1])
        time.sleep(0.1)  # Small delay
        pyautogui.keyUp(paste_keys[0])
        
        time.sleep(delay_between)
        
        # Press Enter to submit
        print("   → Submitting prompt...")
        pyautogui.press('enter')
        
        print("Automation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Automation failed: {e}")
        print("Please manually paste the prompt from clipboard.")
        return False


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
        self.results_dir = Path(RESULTS_DIR) / f"{method_name}_unit"
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
    
    def is_auto_mode_supported(self, ide_name: str) -> bool:
        """Check if auto mode is supported for the given IDE."""
        supported_ides = ['cursor', 'continue', 'cline']
        return ide_name.lower() in supported_ides
    
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
    
    def _get_starter_code_path(self, step_id: str) -> Path:
        """Get the path to the starter code file for a step."""
        return self.method_dir / f"{step_id}_starter_code.py"
    
    def _load_starter_code(self, step_id: str) -> str:
        """Load pre-populated starter code for this step.
        
        The starter code already contains working code from all previous steps,
        so it can be tested independently.
        """
        starter_code_path = self._get_starter_code_path(step_id)
        
        with open(starter_code_path, 'r') as f:
            starter_code = f.read()
        
        starter_code += "\n\n### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###\n"
        
        return starter_code
    
    def _get_step_1_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 1."""
        prompt = []
        prompt.append("STEP 1: Load Triangle Data")
        prompt.append("")
        prompt.append("Load the reported claims triangle from the CSV file and do any necessary data preparation for the chainladder method.")
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
        prompt.append("Calculate volume-weighted average Loss Development Factors using the latest 3 periods.")
        prompt.append("")
        prompt.append("Store the result in a variable called: ldfs_weighted")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_3_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 3."""
        prompt = []
        prompt.append("STEP 3: Calculate Simple Average LDFs")
        prompt.append("")
        prompt.append("Calculate simple average Loss Development Factors using the latest 5 periods.")
        prompt.append("")
        prompt.append("Store the result in a variable called: ldfs_simple")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_4_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 4."""
        prompt = []
        prompt.append("STEP 4: Apply Tail Factor and Calculate CDFs")
        prompt.append("")
        prompt.append("Apply a tail factor of 1.00 from age 132 to ultimate.")
        prompt.append("Calculate the CDFs.")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- triangle_with_tail: triangle with tail factor applied")
        prompt.append("- ldfs_with_tail: LDFs including tail factor")
        prompt.append("- cdfs: CDFs")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_5_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 5."""
        prompt = []
        prompt.append("STEP 5: Calculate Ultimate Claims")
        prompt.append("")
        prompt.append("Use the Chainladder method to calculate ultimate claims for each accident year.")
        prompt.append("Calculate the total ultimate across all years.")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- cl_result: the fitted Chainladder model result")
        prompt.append("- ultimates: ultimate values by accident year")
        prompt.append("- total_ultimate: sum of all ultimates")
        prompt.append("")
        prompt.append("When complete and tested, add this exact line at the end:")
        prompt.append("## STEP COMPLETE - TESTED AND WORKING")
        
        return "\n".join(prompt)
    
    def _get_step_6_prompt(self, step_data: Dict[str, Any]) -> str:
        """Generate prompt for step 6."""
        prompt = []
        prompt.append("STEP 6: Calculate IBNR Reserves")
        prompt.append("")
        prompt.append("Extract IBNR reserves for each accident year and calculate the total.")
        prompt.append("")
        prompt.append("Store the results in variables:")
        prompt.append("- ibnr: IBNR values by accident year")
        prompt.append("- total_ibnr: sum of all IBNR")
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
    
    def run_step(self, step_data: Dict[str, Any], ide_name: str) -> Dict[str, Any]:
        """Run a single step of the test."""
        step_id = step_data["step_id"]
        workspace_dir = self.results_dir / step_id
        
        # Clean and create workspace
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Load pre-populated starter code (includes working code from all previous steps)
        starter_content = self._load_starter_code(step_id)
        solution_path = workspace_dir / STEP_SOLUTION_FILENAME
        with open(solution_path, 'w') as f:
            f.write(starter_content)
        
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
        
        if self.mode == 'auto':
            print(f"3. The system will automatically:")
            if ide_name.lower() == 'continue':
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            elif ide_name.lower() == 'cline':
                print("   - Activate chat (Cmd+' or Ctrl+')")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            else:
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            print(f"4. When complete, add: ## STEP COMPLETE - TESTED AND WORKING")
            
            # Attempt automation
            automation_success = automate_ide_input(full_prompt, ide_name, is_first_question=self.first_question)
            
            # After first step, set flag to False
            if self.first_question:
                self.first_question = False
            
            if not automation_success:
                print("\nFalling back to manual mode...")
                print("Please manually:")
                if ide_name.lower() == 'continue':
                    print(f"- Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                elif ide_name.lower() == 'cline':
                    print(f"- Press Cmd+' (Mac) or Ctrl+' (Windows/Linux) to activate {ide_name} chat")
                    print("- Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
                else:
                    print(f"- Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                    print("- Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
                print("- Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
                print("- Press Enter to submit")
        else:
            print("3. Generate the solution using the prompt from your clipboard:")
            if ide_name.lower() == 'continue':
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
            elif ide_name.lower() == 'cline':
                print(f"   - Press Cmd+' (Mac) or Ctrl+' (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            else:
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            print("   - Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
            print("   - Press Enter to submit")
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
        
        return {
            "step_id": step_id,
            "passed": validation_result["passed"],
            "validation_result": validation_result,
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
        
        # Check if auto mode is supported
        if self.mode == 'auto' and not self.is_auto_mode_supported(ide_name):
            print(f"ERROR: Auto mode is not supported for '{ide_name}'.")
            print("Auto mode is only available for: cursor, continue, cline")
            return
        
        # One-time setup for auto mode
        if self.mode == 'auto' and self.first_question:
            print(f"\nPrepare {ide_name} for automation:")
            print(f"1. Open the workspace folder for the first step in {ide_name}")
            print(f"2. Make sure {ide_name} is open and visible")
            print(f"3. Click on {ide_name} to ensure it's the active window")
            print("Press Ctrl+C anytime to stop")
            input(f"Press Enter when {ide_name} is ready...")
            print("Starting automated test run...")
            
            # Configure pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5
        
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
        
        for i, step in enumerate(steps_to_run):
            print(f"\n{'=' * 80}")
            print(f"Running Step {i+1}/{len(steps_to_run)}: {step['step_id']}")
            print(f"{'=' * 80}")
            
            result = self.run_step(step, ide_name)
            results.append(result)
            
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

