"""
How to use:

MANUAL MODE (default):
- run harness with `python harness.py` or `python harness.py --mode manual`
- Enter the AI name when prompted (or use --ide flag)
- Every time it stops and waits, click into Cursor, do Cmd+L (Mac) or Ctrl+L (Windows/Linux) to start a new chat,
  Cmd+V or Ctrl+V to paste what harness put in clipboard, and enter to let Cursor run.

AUTO MODE (automated):
- run harness with `python harness.py --mode auto`
- Enter the AI name when prompted (or use --ide flag)  
- When prompted, ensure Cursor is the active window and press Enter
- The system will automatically send the key sequence to paste and submit the prompt
- Falls back to manual instructions if automation fails

EXAMPLE USAGE:
python harness.py --mode manual
python harness.py --mode auto --ide Cursor
python harness.py --mode auto
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, List

from utils import parse_multi_part_output


def get_platform_keys():
    """Get the correct key combinations for the current platform."""
    system = platform.system().lower()
    if system == 'darwin':  # macOS
        return {
            'chat_activate': ['command', 'l'],
            'new_chat': ['command', 'n'],
            'paste': ['command', 'v']
        }
    else:  # Windows/Linux
        return {
            'chat_activate': ['ctrl', 'l'],
            'new_chat': ['ctrl', 'n'],
            'paste': ['ctrl', 'v']
        }


def automate_cursor_input(prompt_text, is_first_question=True, delay_before=2.0, delay_between=1.0):
    """Automate the process of pasting prompt into Cursor.
    
    Args:
        prompt_text: The text to paste (should already be in clipboard)
        is_first_question: Whether this is the first question (needs Cmd+L to activate)
        delay_before: Seconds to wait before starting automation
        delay_between: Seconds to wait between key presses
    """
    keys = get_platform_keys()
    
    print("Automating Cursor input...")
    
    # Countdown
    for i in range(int(delay_before), 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1.0)
    
    try:
        # Try to activate Cursor application first (macOS specific)
        system = platform.system().lower()
        if system == 'darwin':
            print("Attempting to activate Cursor application...")
            # Use AppleScript to activate Cursor
            try:
                subprocess.run(['osascript', '-e', 'tell application "Cursor" to activate'], 
                             check=False, capture_output=True)
                time.sleep(1.0)  # Give time for app to activate
            except Exception as e:
                print(f"Could not activate Cursor app: {e}")
                print("Please make sure Cursor is manually focused.")
        
        # Only activate Cursor chat box for the first question
        if is_first_question:
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
        
        # Create new chat
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
        """Check if there's meaningful content below the marker line."""
        marker_line = "### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                # Strip whitespace for comparison to handle leading/trailing spaces
                if marker_line in line.strip():
                    remaining_lines = lines[i+1:]
                    content_lines = [line.strip() for line in remaining_lines if line.strip()]
                    return len(content_lines) > 0
            return False
            
        except (IOError, UnicodeDecodeError):
            return False

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"\nDetected '{self.filename_to_watch}' created.")
            self.file_path = event.src_path
            
            # Check if there's actual content below the marker
            if self._has_content_below_marker(event.src_path):
                print("Content found below marker. File is ready.")
                self.file_ready = True
            else:
                print("No content below marker yet. Waiting for content...")

    def on_modified(self, event):
        """Called when a file is modified (e.g., saved again)."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            
            # Check if there's actual content below the marker
            if self._has_content_below_marker(event.src_path):
                print("Content found below marker. File is ready.")
                self.file_ready = True
            else:
                print("No content below marker yet. Waiting for content...")


# --- Test Harness Engine ---

class IDETestHarness:
    def __init__(self, benchmark_data, mode='manual'):
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR)
        self.benchmark_data = benchmark_data
        self.mode = mode
        self.first_question = True  # Track if this is the first question

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
        prompt.append("3. The code provides path(s) to necessary data files. Import those csv files using pandas or any other method you prefer. You may need to investigate the file structure.")
        prompt.append("4. The code should output the answer to the question in stdout. ")
        prompt.append("5. The code should be inserted BELOW the marker: '### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###' ")

        prompt.append("The answer should be in the following format:")
        if question_type == "multi_part":
            for key in test_case["question_text"]["parts"].keys():
                prompt.append(f"print(f'{key}: {{answer_to_{key}}}:.3f'))")
        elif question_type == "single_part":
            prompt.append("print(f'{answer}:.3f'))")
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
        prompt.append("Nothing else should appear in stdout.")
        prompt.append("6. Do NOT run the script. I will do it on my own.\n")

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
            print("2. Ensure Cursor is the active window (click on it).")
            print("3. The system will automatically:")
            print("   - Activate Cursor chat (Cmd+L)")
            print("   - Create a new chat (Cmd+N)")
            print("   - Paste the prompt (Cmd+V)")
            print("   - Submit the prompt (Enter)")
            print(f"4. Save the final Python code as '{ANSWER_FILENAME}' in the workspace folder when Cursor generates it.")
            
            # Attempt automation (no user prompt needed - already confirmed at start)
            automation_success = automate_cursor_input(prompt, is_first_question=self.first_question)
            
            # After first question, set flag to False
            if self.first_question:
                self.first_question = False
            
            if not automation_success:
                print("\nFalling back to manual mode...")
                print("Please manually:")
                print("- Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate Cursor chat")
                print("- Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
                print("- Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
                print("- Press Enter to submit")
        else:
            print("2. Generate the solution using the prompt from your clipboard:")
            print("   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate Cursor chat")
            print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            print("   - Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
            print("   - Press Enter to submit")
            print(f"3. Save the final Python code as '{ANSWER_FILENAME}' in the workspace folder.")
        
        print(f"\n< Waiting for {ANSWER_FILENAME} to be saved... >")

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
        if execution_error or result.returncode != 0:
            print("Test FAILED: Code execution error occurred")
            if execution_error:
                print(f"Error details: {execution_error}")
            if result.returncode != 0:
                print(f"Process exited with code: {result.returncode}")
            passed = False
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

    def run_all_tests(self, ide_name: str):
        """Runs all tests for a given IDE."""
        # One-time setup for auto mode
        if self.mode == 'auto':
            print("\n=== AUTO MODE SETUP ===")
            print("Please prepare Cursor for automation:")
            print("1. Make sure Cursor is open and visible")
            print("2. Click on Cursor to ensure it's the active window")
            print("3. The automation will handle all questions automatically")
            print("\nOnce you press Enter, the automation will run for ALL test cases.")
            input("Press Enter when Cursor is ready and you're prepared for full automation...")
            print("\n🤖 Starting automated test run...\n")
        
        all_results = {}
        total_points_earned = 0
        total_points_possible = 0
        
        for i, test_case in enumerate(self.benchmark_data):
            question_id = test_case.get('question_id')
            print(
                f"\n--- Running Test {i+1}/{len(self.benchmark_data)}: {question_id} for {ide_name} ---")
            result = self.run_test_case(test_case, ide_name)
            all_results[question_id] = result
            # status = "PASSED" if result["passed"] else "FAILED" # TODO determine what to conclude for multipart questions
            # print(f"--- Result: {status} ---")
            
            # Add to running totals
            total_points_earned += result["points_earned"]
            total_points_possible += result["total_possible_points"]

            print(f"Question Score: {result['points_earned']:.2f}/{result['total_possible_points']:.2f}")

        # Print final summary
        print("\n" + "="*50)
        print("FINAL SCORE SUMMARY")
        print("="*50)
        for key, result in all_results.items():
            print(f"Test ID: {key}, Results: {result['passed']}")
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
        
        percentage = (total_points_earned / total_points_possible * 100) if total_points_possible > 0 else 0
        print("="*50)
        print(f"TOTAL SCORE: {total_points_earned:.2f}/{total_points_possible:.2f} ({percentage:.1f}%)")
        print("="*50)
        
        summary_data = {
            "ide_name": ide_name,
            "total_points_earned": total_points_earned,
            "total_points_possible": total_points_possible,
            "percentage_score": percentage,
            "individual_results": all_results
        }
        
        results_path = os.path.join(RESULTS_DIR, f"summary_{ide_name}.json")
        with open(results_path, 'w') as f:
            json.dump(summary_data, f, indent=4)
        print(f"\nCompleted all tests for {ide_name}. Results saved to {results_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI IDE Test Harness')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation: auto (automated Cursor input) or manual (default)')
    parser.add_argument('--ide', type=str, 
                        help='Name of the AI IDE to test (e.g., Cursor, copilot, etc.)')
    
    args = parser.parse_args()
    
    # from benchmark import benchmark as benchmark_data
    from benchmark_CAS import benchmark_cas as benchmark_data
    harness = IDETestHarness(benchmark_data=benchmark_data, mode=args.mode)

    print(f"Running in {args.mode.upper()} mode")
    if args.mode == 'auto':
        print("Automation will handle Cursor input automatically.")
        # Set pyautogui safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.5  # Default pause between actions
    else:
        print("Manual mode: you will need to paste prompts manually.")

    # You would run this script once for each IDE you want to test.
    # For example, first for "Cursor", then re-run for "VSCode_Copilot".
    ide_to_test = args.ide or input(
        "Enter the name of the AI you are testing (e.g., Cursor, copilot, etc.): ")
    if ide_to_test:
        harness.run_all_tests(ide_to_test)
