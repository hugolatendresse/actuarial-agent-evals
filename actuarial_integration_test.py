"""
Actuarial Integration Test Harness

Tests the AI's ability to perform a complete chainladder analysis in one shot,
rather than step-by-step. This tests end-to-end competency.

Usage:
  python actuarial_integration_test.py --method friedland_xyz_dev_method --ide cursor --mode auto
  python actuarial_integration_test.py --method friedland_xyz_dev_method --ide cursor --mode manual
"""

import json
import subprocess
import os
import shutil
import time
import argparse
import numpy as np
import signal
import sys
import platform
from pathlib import Path
from typing import Dict, Any
import pyperclip
import pyautogui

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


RESULTS_DIR = "ide_results"
SOLUTION_FILENAME = "integration_solution.py"


def get_platform_keys(ide_name=None):
    """Get the correct key combinations for the current platform and IDE."""
    system = platform.system().lower()
    
    if system == 'darwin':
        base_keys = {
            'chat_activate': ['command', 'l'],
            'new_chat': ['command', 'n'],
            'paste': ['command', 'v']
        }
    else:
        base_keys = {
            'chat_activate': ['ctrl', 'l'],
            'new_chat': ['ctrl', 'n'],
            'paste': ['ctrl', 'v']
        }
    
    if ide_name and ide_name.lower() == 'continue':
        base_keys['new_chat'] = None
    elif ide_name and ide_name.lower() == 'cline':
        if system == 'darwin':
            base_keys['chat_activate'] = ['command', '\'']
        else:
            base_keys['chat_activate'] = ['ctrl', '\'']
    
    return base_keys


def automate_ide_input(prompt_text, ide_name, is_first_question=True, delay_before=2.0, delay_between=1.0):
    """Automate the process of pasting prompt into the specified IDE."""
    keys = get_platform_keys(ide_name)
    
    print(f"Automating {ide_name} input...")
    
    for i in range(int(delay_before), 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1.0)
    
    try:
        system = platform.system().lower()
        if system == 'darwin':
            ide_app_name = "Cursor" if ide_name.lower() == "cursor" else ide_name.title()
            print(f"Attempting to activate {ide_app_name} application...")
            try:
                subprocess.run(['osascript', '-e', f'tell application "{ide_app_name}" to activate'], 
                             check=False, capture_output=True)
                time.sleep(1.0)
            except Exception as e:
                print(f"Could not activate {ide_app_name} app: {e}")
        
        should_activate_chat = is_first_question or (ide_name and ide_name.lower() == 'continue')
        if should_activate_chat:
            print("   → Activating chat...")
            chat_keys = keys['chat_activate']
            
            pyautogui.keyDown(chat_keys[0])
            time.sleep(0.1)
            pyautogui.keyDown(chat_keys[1])
            time.sleep(0.1)
            pyautogui.keyUp(chat_keys[1])
            time.sleep(0.1)
            pyautogui.keyUp(chat_keys[0])
            time.sleep(delay_between)
        
        if keys['new_chat'] is not None:
            print("   → Creating new chat...")
            new_chat_keys = keys['new_chat']
            
            pyautogui.keyDown(new_chat_keys[0])
            time.sleep(0.1)
            pyautogui.keyDown(new_chat_keys[1])
            time.sleep(0.1)
            pyautogui.keyUp(new_chat_keys[1])
            time.sleep(0.1)
            pyautogui.keyUp(new_chat_keys[0])
            time.sleep(delay_between)
            
            print("   → Confirming new chat...")
            pyautogui.press('enter')
            time.sleep(delay_between)
        else:
            print("   → Skipping new chat creation (not supported by this IDE)")
            time.sleep(delay_between)
        
        print("   → Pasting prompt...")
        paste_keys = keys['paste']
        
        pyautogui.keyDown(paste_keys[0])
        time.sleep(0.1)
        pyautogui.keyDown(paste_keys[1])
        time.sleep(0.1)
        pyautogui.keyUp(paste_keys[1])
        time.sleep(0.1)
        pyautogui.keyUp(paste_keys[0])
        time.sleep(delay_between)
        
        print("   → Submitting prompt...")
        pyautogui.press('enter')
        
        print("Automation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Automation failed: {e}")
        print("Please manually paste the prompt from clipboard.")
        return False


class SolutionFileHandler(FileSystemEventHandler):
    """Handler that waits for solution file to be created and marked complete."""
    
    def __init__(self, filename_to_watch, workspace_dir):
        self.filename_to_watch = filename_to_watch
        self.workspace_dir = workspace_dir
        self.file_path = None
        self.file_ready = False
    
    def _has_completion_marker(self, file_path):
        """Check if the solution has the completion marker."""
        completion_marker = "## SOLUTION COMPLETE - TESTED AND WORKING"
        
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
                print("'## SOLUTION COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for '## SOLUTION COMPLETE - TESTED AND WORKING' marker...")
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            
            if self._has_completion_marker(event.src_path):
                print("'## SOLUTION COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for '## SOLUTION COMPLETE - TESTED AND WORKING' marker...")


class ActuarialIntegrationTest:
    """Integration test harness for complete actuarial method testing."""
    
    def __init__(self, method_name: str, mode: str = 'manual'):
        self.method_name = method_name
        self.mode = mode
        self.method_dir = Path("test_data") / method_name
        self.results_dir = Path(RESULTS_DIR) / f"{method_name}_integration"
        self.ground_truth = self._load_ground_truth()
        
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    def _create_starter_file(self) -> str:
        """Create the starter file with just imports and data paths."""
        csv_files = sorted(self.method_dir.glob("*.csv"))
        
        lines = []
        lines.append("import pandas as pd")
        lines.append("import numpy as np")
        lines.append("import chainladder as cl")
        lines.append("from pathlib import Path")
        lines.append("")
        lines.append("# Data file paths")
        for i, data_file in enumerate(csv_files):
            abs_path = data_file.resolve()
            # Identify which file is which
            if 'triangle' in data_file.name.lower():
                lines.append(f"triangle_data_path = r'{abs_path}'")
            elif 'premium' in data_file.name.lower():
                lines.append(f"premium_data_path = r'{abs_path}'")
            else:
                lines.append(f"data_path_{i+1} = r'{abs_path}'")
        lines.append("")
        lines.append("### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_prompt(self) -> str:
        """Generate the integration test prompt."""
        prompt = []
        prompt.append("=" * 80)
        prompt.append("INTEGRATION TEST: Complete Chainladder Development Method Analysis")
        prompt.append("=" * 80)
        prompt.append("")
        prompt.append("Perform a complete chainladder analysis to calculate ultimate claims and IBNR")
        prompt.append("reserves for the provided triangle data.")
        prompt.append("")
        prompt.append("=" * 80)
        prompt.append("REQUIREMENTS:")
        prompt.append("=" * 80)
        prompt.append("")
        prompt.append("1. Load the reported claims triangle from triangle_data_path")
        prompt.append("   - Data has development ages in months (12, 24, 36, etc.)")
        prompt.append("   - Convert to chainladder Triangle object (cumulative)")
        prompt.append("   - Age represents months from start of accident year")
        prompt.append("")
        prompt.append("2. Calculate development factors using 3-year volume-weighted averages")
        prompt.append("   - Use chainladder.Development with average='volume' and n_periods=3")
        prompt.append("")
        prompt.append("3. Apply a tail factor of 1.00 from age 132 to ultimate")
        prompt.append("   - Use chainladder.TailConstant(tail=1.0)")
        prompt.append("")
        prompt.append("4. Calculate ultimate claims for each accident year")
        prompt.append("   - Use chainladder.Chainladder model")
        prompt.append("   - Extract from result's ultimate_ attribute")
        prompt.append("")
        prompt.append("5. Calculate IBNR reserves for each accident year")
        prompt.append("   - Extract from result's ibnr_ attribute")
        prompt.append("")
        prompt.append("=" * 80)
        prompt.append("OUTPUT REQUIREMENTS:")
        prompt.append("=" * 80)
        prompt.append("")
        prompt.append("Your code must create these variables:")
        prompt.append("- total_ultimate: sum of ultimate claims across all accident years")
        prompt.append("- total_ibnr: sum of IBNR reserves across all accident years")
        prompt.append("")
        prompt.append("The code should be production-quality and well-structured.")
        prompt.append("")
        prompt.append("=" * 80)
        prompt.append("TESTING WORKFLOW:")
        prompt.append("=" * 80)
        prompt.append("1. Write your code below the marker line")
        prompt.append("2. Test by running: python integration_solution.py")
        prompt.append("3. Debug and fix any errors")
        prompt.append("4. Verify the code runs successfully")
        prompt.append("5. ONLY when working perfectly, add this exact line at the end:")
        prompt.append("   ## SOLUTION COMPLETE - TESTED AND WORKING")
        prompt.append("")
        prompt.append("WARNING: The system evaluates immediately when it sees the completion marker!")
        prompt.append("=" * 80)
        
        return "\n".join(prompt)
    
    def _validate_solution(self, workspace_dir: Path) -> Dict[str, Any]:
        """Validate the integration test solution."""
        validation_code = """
import sys
sys.path.insert(0, '.')
exec(open('integration_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

import numpy as np

# Check required variables exist
assert 'total_ultimate' in dir(), "Variable 'total_ultimate' not found"
assert 'total_ibnr' in dir(), "Variable 'total_ibnr' not found"

print(f"TOTAL_ULTIMATE: {total_ultimate:.2f}")
print(f"TOTAL_IBNR: {total_ibnr:.2f}")
"""
        
        with open(workspace_dir / "validate.py", 'w') as f:
            f.write(validation_code)
        
        result = subprocess.run(
            ["python", "validate.py"],
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
        
        # Parse outputs
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
            
            # Validate against ground truth
            gt_ultimate = self.ground_truth["step_5"]["total_ultimate"]
            gt_ibnr = self.ground_truth["step_6"]["total_ibnr"]
            
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
    
    def run_integration_test(self, ide_name: str):
        """Run the complete integration test."""
        print(f"\nActuarial Integration Test - {self.method_name}")
        print(f"IDE: {ide_name}")
        print(f"Mode: {self.mode}")
        print("=" * 80)
        
        if self.mode == 'auto' and not self.is_auto_mode_supported(ide_name):
            print(f"ERROR: Auto mode is not supported for '{ide_name}'.")
            print("Auto mode is only available for: cursor, continue, cline")
            return
        
        if self.mode == 'auto':
            print(f"\nPrepare {ide_name} for automation:")
            print(f"1. Make sure {ide_name} is open and visible")
            print(f"2. Click on {ide_name} to ensure it's the active window")
            print("Press Ctrl+C to cancel")
            input(f"Press Enter when {ide_name} is ready...")
            print("Starting automated test...")
            
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5
        
        workspace_dir = self.results_dir
        
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        starter_content = self._create_starter_file()
        solution_path = workspace_dir / SOLUTION_FILENAME
        with open(solution_path, 'w') as f:
            f.write(starter_content)
        
        prompt = self._generate_prompt()
        
        try:
            pyperclip.copy(prompt)
            print("Prompt copied to clipboard.")
        except Exception as e:
            print(f"Could not copy to clipboard: {e}")
            print("--- PROMPT ---")
            print(prompt)
            print("--------------")
        
        print("\n--- ACTION REQUIRED ---")
        print(f"Workspace: {workspace_dir.absolute()}")
        print(f"File: {SOLUTION_FILENAME}")
        print(f"1. Open the folder in '{ide_name}'")
        
        if self.mode == 'auto':
            print(f"2. The system will automatically:")
            if ide_name.lower() == 'continue':
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Paste the prompt")
                print("   - Submit the prompt")
            elif ide_name.lower() == 'cline':
                print("   - Activate chat (Cmd+' or Ctrl+')")
                print("   - Create new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt")
                print("   - Submit the prompt")
            else:
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Create new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt")
                print("   - Submit the prompt")
            
            automation_success = automate_ide_input(prompt, ide_name, is_first_question=True)
            
            if not automation_success:
                print("\nFalling back to manual mode...")
                print("Please manually paste and submit the prompt")
        else:
            print("2. Activate chat and paste the prompt from clipboard")
            print("3. Work in integration_solution.py")
        
        print(f"\n< Waiting for {SOLUTION_FILENAME} to be marked complete... >")
        
        event_handler = SolutionFileHandler(SOLUTION_FILENAME, workspace_dir)
        observer = Observer()
        observer.schedule(event_handler, str(workspace_dir), recursive=False)
        observer.start()
        
        try:
            while not event_handler.file_ready:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
        
        print("\n--- Validating Solution ---")
        validation_result = self._validate_solution(workspace_dir)
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        if validation_result["passed"]:
            print("✓ TEST PASSED")
            print(f"\nTotal Ultimate: {validation_result['total_ultimate']:,.2f}")
            print(f"Expected:       {validation_result['expected_ultimate']:,.2f}")
            print(f"\nTotal IBNR:     {validation_result['total_ibnr']:,.2f}")
            print(f"Expected:       {validation_result['expected_ibnr']:,.2f}")
        else:
            print("✗ TEST FAILED")
            if "error" in validation_result and validation_result["error"]:
                print(f"\nError: {validation_result['error']}")
            if "errors" in validation_result and validation_result["errors"]:
                print("\nValidation errors:")
                for error in validation_result["errors"]:
                    print(f"  - {error}")
            if "stdout" in validation_result:
                print(f"\nOutput:\n{validation_result['stdout']}")
        
        print("=" * 80)
        
        result_summary = {
            "method": self.method_name,
            "ide": ide_name,
            "mode": self.mode,
            "passed": validation_result["passed"],
            "validation_details": validation_result,
            "workspace": str(workspace_dir.absolute()),
            "timestamp": time.time()
        }
        
        results_path = self.results_dir / "integration_test_results.json"
        with open(results_path, 'w') as f:
            json.dump(result_summary, f, indent=2)
        
        print(f"Results saved to: {results_path}")
        
        return validation_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Actuarial Integration Test')
    parser.add_argument('--method', type=str, required=True,
                        help='Actuarial method to test (e.g., friedland_xyz_dev_method)')
    parser.add_argument('--ide', type=str, required=True,
                        help='IDE to use (e.g., cursor, continue, cline)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation')
    
    args = parser.parse_args()
    
    integration_test = ActuarialIntegrationTest(args.method, args.mode)
    integration_test.run_integration_test(args.ide)

