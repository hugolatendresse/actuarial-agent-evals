import json
import subprocess
import os
import shutil
import time
import pandas as pd
import numpy as np
import pyperclip
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, List

# TODO format other than .json for benchmarks to allow multi line strings. py files would be good. 
# Can also link to py files and text files in the benchmark.json file.

# TODO look into the following potential other avenues:
# Claude code is like cursor but from the command line. We could have an llm grader look at the command line too and interact with Claude Code https://www.anthropic.com/claude-code
# Janito is an open-source Claude Code https://janito.dev/


ANSWER_FILENAME = "answer.py"
RESULTS_DIR = "ide_results"

# --- File Watcher Handler ---

class SolutionFileHandler(FileSystemEventHandler):
    """
    A handler for watchdog that waits for a specific file to be created.
    """
    def __init__(self, filename_to_watch, workspace_dir):
        self.filename_to_watch = filename_to_watch
        self.workspace_dir = workspace_dir
        self.file_path = None
        self.file_ready = False

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"\n✅ Detected '{self.filename_to_watch}' saved.")
            self.file_path = event.src_path
            self.file_ready = True
    
    def on_modified(self, event):
        """Called when a file is modified (e.g., saved again)."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"✅ Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            self.file_ready = True


# --- Test Harness Engine ---

class IDETestHarness:
    def __init__(self, benchmark_path: str):
        self.benchmark_path = benchmark_path
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR)
        self.benchmark_data = self._load_benchmark()

    def _load_benchmark(self) -> List[Dict[str, Any]]:
        """Loads the JSON benchmark file."""
        try:
            with open(self.benchmark_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise IOError(f"Error loading benchmark file: {e}")
        except Exception as e:
            raise IOError(f"Unexpected error loading benchmark file: {e}")

    def run_test_case(self, test_case: Dict[str, Any], ide_name: str) -> Dict[str, Any]:
        """Runs a single test case using the semi-automated workflow."""
        workspace_dir = os.path.join(RESULTS_DIR, f"{test_case['id']}_{ide_name}")
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
        os.makedirs(workspace_dir)

        # 1. Run setup code to create data files
        if test_case.get("setup_code"):
            setup_script_path = os.path.join(workspace_dir, ANSWER_FILENAME)
            with open(setup_script_path, 'w') as f:
                f.write(test_case["setup_code"] + "\n ### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###\n")
            
            data_file_path = os.path.join(workspace_dir, "data.csv")
            with open(data_file_path, 'w') as f_out:
                subprocess.run(["python", ANSWER_FILENAME], cwd=workspace_dir, check=True, stdout=f_out)

        # 2. Copy prompt to clipboard and wait for user action
        prompt = "I need you to implement the following.\n" + test_case["question_text"] + f"\n Write your code in {RESULTS_DIR}/{test_case['id']}_{ide_name}/{ANSWER_FILENAME}."
        try:
            pyperclip.copy(prompt)
            print("📋 Prompt copied to clipboard.")
        except pyperclip.PyperclipException:
            print("📋 Could not copy to clipboard. Please copy the prompt manually:")
            print("--- PROMPT ---")
            print(prompt)
            print("--------------")


        print("\n--- ACTION REQUIRED ---")
        print(f"Workspace folder: {os.path.abspath(workspace_dir)}")
        print(f"1. Open the folder above in '{ide_name}'.")
        print("2. Generate the solution using the prompt from your clipboard.")
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
        # if not execution_error:
            # try:
        verification_type = test_case["verification"]["type"]
        if verification_type == "python_assertion": # TODO need to fix, worked and then stopped working
            actual_output_obj = eval(program_output_str)
            expected_output_obj = eval(test_case["verification"]["expected_output"])
            eval_scope = {'actual': actual_output_obj, 'expected': expected_output_obj, 'np': np}
            exec(test_case["verification"]["evaluation_script"], eval_scope)
            passed = True
        elif verification_type == "text_output":
            expected_output = test_case["verification"]["expected_output"]
            # if isinstance(expected_output, str): # TODO do we need this?
                # expected_output = expected_output.strip()
            eval_scope = {'actual': program_output_str, 'expected': expected_output, 'np': np}
            exec(test_case["verification"]["evaluation_script"], eval_scope)
            passed = True
        else:
            raise ValueError(f"Unsupported verification type: {verification_type}")
            # except Exception as e:
            #     print(f"Verification failed: {e}")
        
        # 5. Log results
        return {
            "test_id": test_case["id"],
            "ide_name": ide_name,
            "passed": passed,
            "prompt": prompt,
            "actual_output": program_output_str,
            "expected_output": test_case["verification"]["expected_output"],
            "execution_error": execution_error,
        }

    def run_all_tests(self, ide_name: str):
        """Runs all tests for a given IDE."""
        all_results = []
        for i, test_case in enumerate(self.benchmark_data):
            print(f"\n--- Running Test {i+1}/{len(self.benchmark_data)}: {test_case['id']} for {ide_name} ---")
            result = self.run_test_case(test_case, ide_name)
            all_results.append(result)
            status = "PASSED" if result["passed"] else "FAILED"
            print(f"--- Result: {status} ---")

        results_path = os.path.join(RESULTS_DIR, f"summary_{ide_name}.json")
        with open(results_path, 'w') as f:
            json.dump(all_results, f, indent=4)
        print(f"\nCompleted all tests for {ide_name}. Results saved to {results_path}")


if __name__ == '__main__':
    benchmark_file = "benchmark.json"
    harness = IDETestHarness(benchmark_path=benchmark_file)
    
    # You would run this script once for each IDE you want to test.
    # For example, first for "Cursor", then re-run for "VSCode_Copilot".
    ide_to_test = input("Enter the name of the IDE you are testing (e.g., Cursor, VSCode_Copilot): ")
    if ide_to_test:
        harness.run_all_tests(ide_to_test)

