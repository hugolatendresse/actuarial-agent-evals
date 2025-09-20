"""
How to use:

MANUAL MODE (default):
- run harness with `python harness.py` or `python harness.py --mode manual`
- Enter the AI name when prompted (or use --ide flag)
- Every time it stops and waits, click into the IDE, activate chat, and paste the prompt
- For Cursor: Cmd+L (Mac) or Ctrl+L (Windows/Linux) to start chat, then Cmd+N/Ctrl+N for new chat
- For Continue: Only Cmd+L (Mac) or Ctrl+L (Windows/Linux) to start chat (no new chat needed)
- For Cline: Cmd+' (Mac) or Ctrl+' (Windows/Linux) to start chat, then Cmd+N/Ctrl+N for new chat

AUTO MODE (automated):
- run harness with `python harness.py --mode auto`
- Only supported for Cursor, Continue, and Cline IDEs
- Enter the AI name when prompted (or use --ide flag)  
- When prompted, ensure the IDE is the active window and press Enter
- The system will automatically send the appropriate key sequence based on the IDE
- Falls back to manual instructions if automation fails

EXAMPLE USAGE:
python harness.py --mode manual --ide continue
python harness.py --mode auto --ide cursor
python harness.py --mode auto --ide continue
python harness.py --mode auto --ide cline
python harness.py --mode manual --ide cursor --question-id EX5-F19-Q01
python harness.py --mode auto --ide cursor --start-from EX5-F19-Q05
"""

import json
import subprocess
import csv
import os
import shutil
import time
import platform
import argparse
import pandas as pd
import numpy as np
import pyperclip
import pyautogui
import signal
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, List

from utils import parse_multi_part_output


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
        # For Cline, use Cmd+' (or Ctrl+') to activate chat, Cmd+N for new chat (add as custom shortcut)
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


# TODO format other than .json for benchmarks to allow multi line strings. py files would be good.
# Can also link to py files and text files in the benchmark.json file.

# TODO look into the following potential other avenues:
# Claude code is like cursor but from the command line. We could have an llm grader look at the command line too and interact with Claude Code https://www.anthropic.com/claude-code
# Janito is an open-source Claude Code https://janito.dev/


ANSWER_FILENAME = "answer.py"
RESULTS_DIR = "ide_results"


def write_data_to_csv(data_list, output_file="data.csv"):
    if data_list:
        assert isinstance(
            data_list, list), "Data should be a list of dictionaries"
        assert all(isinstance(item, dict)
                   for item in data_list), "Each item in the list should be a dictionary"

        # Get headers from the keys of the first dictionary
        headers = list(data_list[0].keys())

        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)

        print(f"Data has been saved to {output_file}")
        print(f"Extracted headers: {headers}")
    else:
        print("The data list is empty, no CSV file created.")


class SolutionFileHandler(FileSystemEventHandler):
    """
    A handler for watchdog that waits for a specific file to be created.
    """

    def __init__(self, filename_to_watch, workspace_dir):
        self.filename_to_watch = filename_to_watch
        self.workspace_dir = workspace_dir
        self.file_path = None
        self.file_ready = False

    def _has_content_below_marker(self, file_path):
        """Check if there's meaningful content below the marker line and if solution is complete."""
        marker_line = "### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###"
        completion_marker = "## SOLUTION COMPLETE - TESTED AND WORKING"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the start marker
            marker_index = content.find(marker_line)
            if marker_index == -1:
                return False
            
            # Get content after the marker
            content_after_marker = content[marker_index + len(marker_line):]
            
            # Check if there's meaningful content
            content_lines = [line.strip() for line in content_after_marker.split('\n') if line.strip()]
            has_content = len(content_lines) > 0
            
            # Check for completion marker
            has_completion_marker = completion_marker in content_after_marker
            
            return has_content and has_completion_marker
            
        except (IOError, UnicodeDecodeError):
            return False

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"\nDetected '{self.filename_to_watch}' created.")
            self.file_path = event.src_path
            
            # Check if there's actual content below the marker and completion marker
            if self._has_content_below_marker(event.src_path):
                print("Content and '## SOLUTION COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for content and '## SOLUTION COMPLETE - TESTED AND WORKING' marker...")

    def on_modified(self, event):
        """Called when a file is modified (e.g., saved again)."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            
            # Check if there's actual content below the marker and completion marker
            if self._has_content_below_marker(event.src_path):
                print("Content and '## SOLUTION COMPLETE - TESTED AND WORKING' marker found. File is ready.")
                self.file_ready = True
            else:
                print("Waiting for content and '## SOLUTION COMPLETE - TESTED AND WORKING' marker...")


# --- Test Harness Engine ---

class IDETestHarness:
    def __init__(self, benchmark_data, mode='manual', state_file=None):
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR)
        self.benchmark_data = benchmark_data
        self.mode = mode
        self.first_question = True  # Track if this is the first question
        self.state_file = state_file or os.path.join(RESULTS_DIR, "harness_state.json")
        self.completed_tests = {}
        self.total_points_earned = 0
        self.total_points_possible = 0
        self.current_question = None
        self.ide_name = None
        
        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C by saving state and exiting."""
        print("\nInterruption detected. Saving progress...")
        self.save_state()
        print(f"Progress saved. Score: {self.total_points_earned:.2f}/{self.total_points_possible:.2f}")
        print(f"To resume: python harness.py --mode {self.mode} --ide {self.ide_name} --resume")
        sys.exit(0)
    
    def save_state(self):
        """Save current test progress to state file."""
        state = {
            "completed_tests": self.completed_tests,
            "total_points_earned": self.total_points_earned,
            "total_points_possible": self.total_points_possible,
            "first_question": self.first_question,
            "current_question": self.current_question,
            "ide_name": self.ide_name,
            "mode": self.mode,
            "timestamp": time.time()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=4)
    
    def load_state(self):
        """Load previous test progress from state file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.completed_tests = state.get("completed_tests", {})
                    self.total_points_earned = state.get("total_points_earned", 0)
                    self.total_points_possible = state.get("total_points_possible", 0)
                    self.first_question = state.get("first_question", True)
                    self.current_question = state.get("current_question")
                    
                    print(f"Loaded previous session: {len(self.completed_tests)}/{len(self.benchmark_data)} questions completed")
                    print(f"Current score: {self.total_points_earned:.2f}/{self.total_points_possible:.2f}")
                    return True
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading state file: {e}")
        return False
    
    def clear_state(self):
        """Clear saved state file."""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
    
    def get_remaining_tests(self, start_from=None, question_id=None):
        """Get list of tests to run, optionally starting from specific question or running single question."""
        if question_id:
            # Return only the specific question
            matching_test = next((test for test in self.benchmark_data 
                                if test.get('question_id') == question_id), None)
            if matching_test is None:
                print(f"Question '{question_id}' not found in benchmark")
                return []
            return [matching_test]
        
        if start_from:
            start_idx = next((i for i, test in enumerate(self.benchmark_data) 
                            if test.get('question_id') == start_from), None)
            if start_idx is None:
                print(f"Question '{start_from}' not found in benchmark")
                return []
            return self.benchmark_data[start_idx:]
        
        return [test for test in self.benchmark_data 
                if test.get('question_id') not in self.completed_tests]
    
    def is_auto_mode_supported(self, ide_name: str) -> bool:
        """Check if auto mode is supported for the given IDE."""
        supported_ides = ['cursor', 'continue', 'cline']
        return ide_name.lower() in supported_ides

    def calculate_question_score(self, test_case: Dict[str, Any], passed_result) -> tuple:
        """
        Calculate the score for a single question.
        Returns (points_earned, total_possible_points)
        """
        question_point_value = test_case.get("question_point_value", 0)
        
        if isinstance(question_point_value, (int, float)):
            if passed_result is True:
                return (question_point_value, question_point_value)
            else:
                return (0, question_point_value)
        
        elif isinstance(question_point_value, dict):
            total_possible = sum(question_point_value.values())
            points_earned = 0
            
            if isinstance(passed_result, dict):
                for part_key, part_passed in passed_result.items():
                    if part_passed and part_key in question_point_value:
                        points_earned += question_point_value[part_key]
            
            return (points_earned, total_possible)
        
        else:
            return (0, 0)

    def _load_benchmark(self) -> List[Dict[str, Any]]:
        """Loads the py benchmark file."""
        try:
            with open(self.benchmark_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise IOError(f"Error loading benchmark file: {e}")
        except Exception as e:
            raise IOError(f"Unexpected error loading benchmark file: {e}")

    def run_test_case(self, test_case: Dict[str, Any], ide_name: str) -> Dict[str, Any]:
        """Runs a single test case using the semi-automated workflow."""
        workspace_dir = os.path.join(
            RESULTS_DIR, f"{test_case.get('question_id')}_{ide_name}")
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
        os.makedirs(workspace_dir)

        question_type = test_case["question_text"]["type"]

        # parse data
        single_values = {}
        csv_files_paths = []
        csv_counter = 0
        notes = []
        for input_dict in test_case.get("inputs", []):
            if input_dict["type"] == "table":
                # TODO if multiple tables, they will be overwritten
                csv_counter += 1
                data_file_path = os.path.abspath(os.path.join(
                    workspace_dir, f"data_{csv_counter}.csv"))
                write_data_to_csv(input_dict.get(
                    "data", []), data_file_path)
                csv_files_paths.append(data_file_path)
            elif input_dict["type"] == "python_code":
                raise NotImplementedError()
            elif input_dict["type"] == "single_value":
                single_values[input_dict["name"]] = input_dict["data"]
            elif input_dict["type"] == "single_date":
                single_values[input_dict["name"]] = f'"{input_dict["data"]}"'
            elif input_dict["type"] == "notes":
                if isinstance(input_dict["data"], list):
                    notes.extend(input_dict["data"])
                else:
                    notes.append(input_dict["data"])
            else:
                raise ValueError(
                    f"Unsupported input type: {input_dict['type']}")

        script = []

        if csv_files_paths:
            script.append(
                "# Filepaths to data files (to be loaded with pandas)")
            for i, filepath in enumerate(csv_files_paths):
                script.append(f"data_path{i} = r'{filepath}'")
            script.append("")

        if single_values:
            script.append("# Variables to use")
            for varname, value in single_values.items():
                script.append(f"{varname} = {value}")
            script.append("")

        if "setup_code" in test_case:
            script.append(test_case["setup_code"])

        script.append(
            "\n ### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###\n")
        setup_script_path = os.path.join(workspace_dir, ANSWER_FILENAME)
        with open(setup_script_path, 'w') as f:
            f.write("\n".join(script))

        # with open(data_file_path, 'w') as f_out:  # TODO will we ever need to run setup code?
        #     subprocess.run(["python", ANSWER_FILENAME],
        #                    cwd=workspace_dir, check=True, stdout=f_out)

        # 2. Copy prompt to clipboard and wait for user action
        prompt = []
        prompt.append(test_case["question_text"]["prompt"])

        if question_type == "multi_part":
            for key, part in test_case["question_text"]["parts"].items():
                prompt.append(f"{key}: {part}")
            prompt.append("")

        if notes:
            prompt.append(
                "--- Important notes to answer the question ---")
            prompt.append("")
            for note in notes:
                prompt.append(note)
            prompt.append("")

        prompt.append(
            "--- You will need to answer the question by doing the following steps. ---")
        prompt.append(
            f"1. Write Python code to solve the question in {RESULTS_DIR}/{test_case.get('question_id')}_{ide_name}/{ANSWER_FILENAME}.")
        prompt.append(
            "2. The file I just specified already contains data. Your code should directly use that data.")
        # TODO only mention data if the problem has data to be included directly in the code.
        prompt.append("Do not modify the existing data.")
        prompt.append("3. The code provides path(s) to necessary data files. Import those csv files using pandas or any other method you prefer. ")
        prompt.append("4. If there are data files, you need to read them to understand the structure/content.")
        prompt.append("5. ITERATIVE DEVELOPMENT: You may run and test your code multiple times to debug and refine your solution.")
        prompt.append("6. You should go ahead and modify the answer.py file rather than just showing or proposing the code.")
        prompt.append("7. The code should be inserted BELOW the marker: '### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###' ")
        prompt.append("8. The code should output the answer to the question in stdout. ")
        prompt.append("9. IMPORTANT: Do NOT round your calculations or intermediate results. Use full precision in your calculations. Only the final display format should round to 3 decimal places.")

        prompt.append("The answer should be in the following format:")
        if question_type == "multi_part":
            for key in test_case["question_text"]["parts"].keys():
                prompt.append(f"print(f'{key}: {{answer_to_{key}}}:.3f'))")
        elif question_type == "single_part":
            prompt.append("print(f'{answer}:.3f'))")
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
        prompt.append("Nothing else should appear in stdout.")
        
        prompt.append("")
        prompt.append("=" * 60)
        prompt.append("MANDATORY TESTING WORKFLOW - FOLLOW EXACTLY:")
        prompt.append("=" * 60)
        prompt.append("10. Write your initial code in answer.py")
        prompt.append("11. Save the file WITHOUT any completion marker")
        prompt.append("12. Run the command: python answer.py")
        prompt.append("13. Check if the output matches the required format exactly")
        prompt.append("14. If there are errors or wrong output:")
        prompt.append("    - Read the error messages carefully")
        prompt.append("    - Fix the code")
        prompt.append("    - Save the file again")
        prompt.append("    - Run python answer.py again")
        prompt.append("15. Repeat step 14 until the code runs perfectly")
        prompt.append("16. ONLY WHEN your code runs without errors AND produces correct output:")
        prompt.append("    Add this exact line at the end: ## SOLUTION COMPLETE - TESTED AND WORKING")
        prompt.append("")
        prompt.append("WARNING: Adding the completion marker before testing will cause failure!")
        prompt.append("The system will immediately evaluate your code when it sees the marker!")
        prompt.append("=" * 60)

        # Combine prompt into a single string and put in clipboard
        prompt = "\n".join(prompt)
        try:
            pyperclip.copy(prompt)
            print("Prompt copied to clipboard.")
        except pyperclip.PyperclipException:
            print("Could not copy to clipboard. Please copy the prompt manually:")
            print("--- PROMPT ---")
            print(prompt)
            print("--------------")

        print("\n--- ACTION REQUIRED ---")
        print(f"Workspace folder: {os.path.abspath(workspace_dir)}")
        print(f"1. Open the folder above in '{ide_name}'.")
        
        if self.mode == 'auto':
            print(f"2. Ensure {ide_name} is the active window (click on it).")
            print("3. The system will automatically:")
            if ide_name.lower() == 'continue':
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            elif ide_name.lower() == 'cline':
                print("   - Activate chat (Cmd+' or Ctrl+')")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            else:  # cursor or other supported IDEs
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            print(f"4. Save the final Python code as '{ANSWER_FILENAME}' in the workspace folder when {ide_name} generates it.")
            
            # Attempt automation (no user prompt needed - already confirmed at start)
            automation_success = automate_ide_input(prompt, ide_name, is_first_question=self.first_question)
            
            # After first question, set flag to False
            if self.first_question:
                self.first_question = False
            
            if not automation_success:
                print("\nFalling back to manual mode...")
                print("Please manually:")
                if ide_name.lower() == 'continue':
                    print(f"- Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat (needed for each question)")
                elif ide_name.lower() == 'cline':
                    print(f"- Press Cmd+' (Mac) or Ctrl+' (Windows/Linux) to activate {ide_name} chat")
                    print("- Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
                else:
                    print(f"- Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                    print("- Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
                print("- Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
                print("- Press Enter to submit")
        else:
            print("2. Generate the solution using the prompt from your clipboard:")
            if ide_name.lower() == 'continue':
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat (needed for each question)")
            elif ide_name.lower() == 'cline':
                print(f"   - Press Cmd+' (Mac) or Ctrl+' (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            else:
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            print("   - Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
            print("   - Press Enter to submit")
            print(f"3. Save the final Python code as '{ANSWER_FILENAME}' in the workspace folder.")
        
        print(f"\n< Waiting for {ANSWER_FILENAME} to be saved with '## SOLUTION COMPLETE - TESTED AND WORKING' marker... >")

        # Set up the file watcher
        event_handler = SolutionFileHandler(ANSWER_FILENAME, workspace_dir)
        observer = Observer()
        observer.schedule(event_handler, workspace_dir, recursive=False)
        observer.start()

        try:
            while not event_handler.file_ready:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

        # 3. Execute the user-generated code
        result = subprocess.run(
            ["python", ANSWER_FILENAME],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        program_output_str = result.stdout.strip()
        execution_error = result.stderr.strip()

        print("\n--- Execution Result ---")
        if execution_error:
            print(f"Execution error: {execution_error}")
        else:
            print(f"Output: {program_output_str}")

        # 4. Verify the result
        passed = False
        
        # Check for execution errors first
        if result.returncode != 0:
            print("Test FAILED: Code execution error occurred")
            print(f"Process exited with code: {result.returncode}")
            if execution_error:
                print(f"Error details: {execution_error}")
            passed = False
        elif execution_error and ("Error" in execution_error or "Traceback" in execution_error):
            # Only treat stderr as error if it contains actual error messages (not just warnings)
            print("Test FAILED: Code execution error occurred")
            print(f"Error details: {execution_error}")
            passed = False
        elif execution_error:
            # Just warnings - log them but don't fail the test
            print(f"Warnings (not errors): {execution_error}")
            # Continue to verification logic below
        elif not program_output_str.strip():
            print("Test FAILED: Code executed but produced no output")
            passed = False
        else:
            # Code executed successfully, proceed with verification
            try:
                verification_type = test_case["expected_answer"]["type"]
                if verification_type == "python_assertion":  # TODO probably broken with new benchmark format
                    actual_output_obj = eval(program_output_str)
                    expected_output_obj = eval(
                        test_case["verification"]["expected_output"])
                    eval_scope = {'actual': actual_output_obj,
                              'expected': expected_output_obj, 'np': np}
                    exec(test_case["verification"]["evaluation_script"], eval_scope)
                    passed = True
                elif verification_type == "text_output":  # TODO probably broken with new benchmark format
                    expected_output = test_case["verification"]["expected_output"]
                    # if isinstance(expected_output, str): # TODO do we need this?
                    # expected_output = expected_output.strip()
                    eval_scope = {'actual': program_output_str,
                              'expected': expected_output, 'np': np}
                    exec(test_case["verification"]["evaluation_script"], eval_scope)
                    passed = True
                elif verification_type == "point_estimate":
                    # TODO generalize
                    expected_value = test_case["expected_answer"]['value']
                    tolerance = test_case["expected_answer"]['tolerance']
                    # Get actual value by parsing the output from stdout
                    try:
                        actual_value = float(program_output_str)
                        print("Expected value:", expected_value)
                        print("Tolerance:", tolerance)
                        print("Actual value:", actual_value)
                        if abs(actual_value - expected_value) <= tolerance:
                            print("Test passed!")
                            passed = True
                        else:
                            print(
                                f"Test failed! Expected value within {tolerance} of {expected_value}, but got {actual_value}.")
                            passed = False
                    except ValueError as e:
                        print(f"Test FAILED: Could not parse output as number. Output was: '{program_output_str}'")
                        print(f"Parsing error: {e}")
                        passed = False
                elif verification_type == "multi_part_numeric":
                    try:
                        actual = parse_multi_part_output(program_output_str, list(
                            test_case["expected_answer"]["parts"].keys()))
                        expected = test_case["expected_answer"]["parts"]
                        passed = {}  # TODO those should be points? Out of 1? Out of 4?
                        for key in expected.keys():
                            if key not in actual:
                                print(f"Missing key in actual output: {key}")
                                passed[key] = False
                                break
                            actual_val = actual[key]
                            expected_val = expected[key]['value']
                            if not np.isclose(actual_val, expected_val, atol=expected[key].get('tolerance', 1e-5)):
                                print(
                                    f"Value for '{key}' does not match: expected {expected_val}, got {actual_val}")
                                passed[key] = False  # TODO
                            else:
                                print(
                                    f"Value for '{key}' matches! expected {expected_val}, got {actual_val}")
                                passed[key] = True
                    except Exception as e:
                        print(f"Test FAILED: Could not parse multi-part output. Output was: '{program_output_str}'")
                        print(f"Parsing error: {e}")
                        passed = False

                else:
                    raise ValueError(
                        f"Unsupported verification type: {verification_type}")
            except Exception as e:
                print(f"Test FAILED: Verification failed with error: {e}")
                passed = False

        # Calculate score for this question
        points_earned, total_possible = self.calculate_question_score(test_case, passed)
        
        # 5. Log results
        return {
            "test_id": test_case.get("question_id"),
            "ide_name": ide_name,
            "passed": passed,
            "points_earned": points_earned,
            "total_possible_points": total_possible,
            "prompt": prompt,
            "actual_output": program_output_str,
            "expected_output": test_case["expected_answer"],
            "execution_error": execution_error,
        }

    def run_all_tests(self, ide_name: str, start_from=None, question_id=None, resume=False):
        """Runs all tests for a given IDE with resume support."""
        self.ide_name = ide_name
        
        # Validate mutually exclusive options
        if question_id and start_from:
            print("ERROR: Cannot use both --question-id and --start-from options together")
            return
        
        if question_id and resume:
            print("ERROR: Cannot use --question-id with --resume option")
            return
        
        # Handle resume mode
        if resume:
            if self.load_state():
                remaining = self.get_remaining_tests()
                if not remaining:
                    print("All tests already completed!")
                    self.show_final_summary(ide_name, partial=False)
                    return
                # When resuming, treat as first question for automation purposes
                self.first_question = True
            else:
                print("No previous state found, starting fresh")
                resume = False
        
        if not resume:
            self.clear_state()
        
        # Check if auto mode is supported for this IDE
        if self.mode == 'auto' and not self.is_auto_mode_supported(ide_name):
            print(f"ERROR: Auto mode is not supported for '{ide_name}'.")
            print("Auto mode is only available for: cursor, continue, cline")
            return
        
        # One-time setup for auto mode
        if self.mode == 'auto' and self.first_question:
            print(f"Prepare {ide_name} for automation:")
            print(f"1. Make sure {ide_name} is open and visible")
            print(f"2. Click on {ide_name} to ensure it's the active window")
            print("Press Ctrl+C anytime to stop and save progress")
            input(f"Press Enter when {ide_name} is ready...")
            print("Starting automated test run...")
        
        # Get tests to run
        tests_to_run = self.get_remaining_tests(start_from, question_id)
        if not tests_to_run:
            if question_id:
                print(f"Question '{question_id}' not found!")
            else:
                print("No tests to run!")
            return
        
        if question_id:
            print(f"Running single question: {question_id}")
        else:
            print(f"Running {len(tests_to_run)} tests. Press Ctrl+C to interrupt.")
        
        try:
            for test_case in tests_to_run:
                current_question_id = test_case.get('question_id')
                self.current_question = current_question_id
                
                if question_id:
                    print(f"\nRunning: {current_question_id}")
                else:
                    print(f"\nRunning: {current_question_id} ({len(self.completed_tests) + 1}/{len(self.benchmark_data)})")
                
                result = self.run_test_case(test_case, ide_name)
                
                # Store result and update totals
                self.completed_tests[current_question_id] = result
                self.total_points_earned += result["points_earned"]
                self.total_points_possible += result["total_possible_points"]
                
                print(f"Score: {result['points_earned']:.2f}/{result['total_possible_points']:.2f}")
                
                # Save progress after each question
                self.save_state()
                
                if self.first_question:
                    self.first_question = False
                
                self.current_question = None
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            return
        
        # All tests completed
        if question_id:
            print("Question completed!")
        else:
            print("All tests completed!")
        self.show_final_summary(ide_name, partial=False)
        if not question_id:
            self.clear_state()
    
    def show_final_summary(self, ide_name: str, partial: bool = False):
        """Show final score summary."""
        status = "PARTIAL RESULTS" if partial else "FINAL RESULTS"
        print(f"\n{status}")
        print("="*50)
        
        for key, result in self.completed_tests.items():
            status_str = ""
            if isinstance(result['passed'], dict):
                passed_parts = sum(1 for v in result['passed'].values() if v)
                total_parts = len(result['passed'])
                status_str = f"({passed_parts}/{total_parts} parts)"
            elif result['passed']:
                status_str = "PASSED"
            else:
                status_str = "FAILED"
            
            print(f"{key}: {result['points_earned']:.2f}/{result['total_possible_points']:.2f} {status_str}")
        
        percentage = (self.total_points_earned / self.total_points_possible * 100) if self.total_points_possible > 0 else 0
        print("="*50)
        print(f"TOTAL: {self.total_points_earned:.2f}/{self.total_points_possible:.2f} ({percentage:.1f}%)")
        
        if partial:
            remaining = len(self.benchmark_data) - len(self.completed_tests)
            print(f"Remaining: {remaining}")
        
        print("="*50)
        
        # Save results
        suffix = "_partial" if partial else ""
        results_path = os.path.join(RESULTS_DIR, f"summary_{ide_name}{suffix}.json")
        summary_data = {
            "ide_name": ide_name,
            "total_points_earned": self.total_points_earned,
            "total_points_possible": self.total_points_possible,
            "percentage_score": percentage,
            "completed_tests": len(self.completed_tests),
            "total_tests": len(self.benchmark_data),
            "individual_results": self.completed_tests,
            "is_partial": partial,
            "timestamp": time.time()
        }
        
        with open(results_path, 'w') as f:
            json.dump(summary_data, f, indent=4)
        print(f"Results saved to {results_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI IDE Test Harness')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation: auto (automated) or manual (default)')
    parser.add_argument('--ide', type=str, 
                        help='Name of the AI tool to test')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from previous session')
    parser.add_argument('--start-from', type=str,
                        help='Start from specific question ID')
    parser.add_argument('--question-id', type=str,
                        help='Run only a specific question ID')
    parser.add_argument('--state-file', type=str,
                        help='Path to state file (default: ide_results/harness_state.json)')
    
    args = parser.parse_args()
    
    from benchmark_CAS import benchmark_cas as benchmark_data
    harness = IDETestHarness(benchmark_data=benchmark_data, mode=args.mode, 
                           state_file=args.state_file)

    print(f"Running in {args.mode.upper()} mode")
    if args.mode == 'auto':
        print("Press Ctrl+C anytime to stop and save progress.")
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    else:
        print("Press Ctrl+C anytime to stop and save progress.")

    # Validate mutually exclusive options
    if args.question_id and args.start_from:
        print("ERROR: Cannot use both --question-id and --start-from options together")
        sys.exit(1)
    
    if args.question_id and args.resume:
        print("ERROR: Cannot use --question-id with --resume option")
        sys.exit(1)
    
    ide_to_test = args.ide or input("Enter the name of the AI you are testing: ")
    if ide_to_test:
        harness.run_all_tests(ide_to_test, start_from=args.start_from, question_id=args.question_id, resume=args.resume)
