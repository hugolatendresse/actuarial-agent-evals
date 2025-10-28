import signal
import sys
import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
import pyautogui

from test_framework.base import FileWatcher, IDEAutomation, WorkspaceManager, PromptHandler
from test_framework.method_config import MethodConfig


class BaseTestHarness(ABC):
    """Abstract base class for test harnesses."""
    
    COMPLETION_MARKER = "## SOLUTION COMPLETE - TESTED AND WORKING"
    RESULTS_DIR_NAME = "ide_results"
    
    def __init__(self, config: MethodConfig, mode: str = 'manual'):
        self.config = config
        self.mode = mode
        self.results_base_dir = Path(self.RESULTS_DIR_NAME)
        self.ground_truth = config.load_ground_truth()
        self.first_question = True
        
        if not self.results_base_dir.exists():
            self.results_base_dir.mkdir(parents=True, exist_ok=True)
        
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\nInterruption detected. Exiting...")
        sys.exit(0)
    
    def is_auto_mode_supported(self, ide_name: str) -> bool:
        """Check if auto mode is supported for the given IDE."""
        return IDEAutomation.is_supported(ide_name)
    
    def prepare_auto_mode(self, ide_name: str) -> None:
        """Prepare for automated test execution."""
        if not self.first_question:
            return
        
        print(f"\nPrepare {ide_name} for automation:")
        print(f"1. Make sure {ide_name} is open and visible")
        print(f"2. Click on {ide_name} to ensure it's the active window")
        print("Press Ctrl+C anytime to stop")
        input(f"Press Enter when {ide_name} is ready...")
        print("Starting automated test run...")
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def deliver_prompt(self, prompt: str, ide_name: str) -> bool:
        """Copy prompt to clipboard and optionally automate delivery."""
        PromptHandler.copy_to_clipboard(prompt)
        
        if self.mode == 'auto':
            success = IDEAutomation.automate_input(
                prompt,
                ide_name,
                is_first_question=self.first_question,
            )
            
            if self.first_question:
                self.first_question = False
            
            if not success:
                print("\nFalling back to manual mode...")
                return False
        
        return True
    
    def wait_for_solution(
        self,
        workspace_dir: Path,
        filename: str
    ) -> Path:
        """Wait for solution file to be created and marked complete."""
        print(f"\n< Waiting for {filename} to be marked complete... >")
        
        watcher = FileWatcher(filename, workspace_dir, self.COMPLETION_MARKER)
        return watcher.wait_for_completion()
    
    @abstractmethod
    def run(self, ide_name: str, **kwargs) -> Dict[str, Any]:
        """Run the test harness."""
        pass


class UnitTestHarness(BaseTestHarness):
    """Test harness for step-by-step unit testing."""
    
    COMPLETION_MARKER = "## STEP COMPLETE - TESTED AND WORKING"
    SOLUTION_FILENAME = "step_solution.py"
    MARKER_LINE = "### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###"
    
    def __init__(self, config: MethodConfig, mode: str = 'manual'):
        super().__init__(config, mode)
        self.results_dir = self.results_base_dir / f"{config.method_name}_unit"
        
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_starter_code_path(self, step_id: str) -> Path:
        """Get the path to the starter code file for a step."""
        return self.config.test_data_dir / f"{step_id}_starter_code.py"
    
    def _load_starter_code(self, step_id: str) -> str:
        """Load pre-populated starter code for this step."""
        starter_code_path = self._get_starter_code_path(step_id)
        
        with open(starter_code_path, 'r') as f:
            starter_code = f.read()
        
        if self.MARKER_LINE not in starter_code:
            starter_code += f"\n\n{self.MARKER_LINE}\n"
        
        return starter_code
    
    def _build_full_prompt(
        self,
        step_id: str,
        description: str,
        step_prompt: str,
        workspace_dir: Path
    ) -> str:
        """Build complete prompt with standard testing instructions."""
        lines = []
        lines.append(step_prompt)
        lines.append("")
        lines.append("MANDATORY WORKFLOW:")
        lines.append(f"1. Work in file: {workspace_dir / self.SOLUTION_FILENAME}")
        lines.append("2. Write your code BELOW the marker line")
        lines.append("3. Test your code by running it: python step_solution.py")
        lines.append("4. Fix any errors and test again")
        lines.append("5. ONLY when working perfectly, add this line at the end:")
        lines.append(f"   {self.COMPLETION_MARKER}")
        lines.append("")
        lines.append("WARNING: The system evaluates immediately when it sees the completion marker!")
        
        return "\n".join(lines)
    
    def run_step(self, step_config: Dict[str, Any], ide_name: str) -> Dict[str, Any]:
        """Run a single test step."""
        step_id = step_config["step_id"]
        workspace_dir = self.results_dir / step_id
        
        WorkspaceManager.create_workspace(workspace_dir, clean=True)
        
        starter_content = self._load_starter_code(step_id)
        solution_path = workspace_dir / self.SOLUTION_FILENAME
        WorkspaceManager.write_file(solution_path, starter_content)
        
        prompt = step_config["prompt_template"](step_config)
        full_prompt = self._build_full_prompt(
            step_id,
            step_config["description"],
            prompt,
            workspace_dir
        )
        
        PromptHandler.display_instructions(
            workspace_dir,
            self.SOLUTION_FILENAME,
            ide_name,
            self.mode,
            self.first_question
        )
        
        self.deliver_prompt(full_prompt, ide_name)
        self.wait_for_solution(workspace_dir, self.SOLUTION_FILENAME)
        
        print("\n--- Validating Solution ---")
        validation_result = step_config["validation"](workspace_dir)
        
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
    
    def run(
        self,
        ide_name: str,
        start_from: Optional[str] = None,
        single_step: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run all steps or specific step(s)."""
        print(f"\nActuarial Unit Test Harness - {self.config.display_name}")
        print(f"IDE: {ide_name}")
        print(f"Mode: {self.mode}")
        print("=" * 80)
        
        if self.mode == 'auto' and not self.is_auto_mode_supported(ide_name):
            print(f"ERROR: Auto mode is not supported for '{ide_name}'.")
            print(f"Auto mode is only available for: {', '.join(IDEAutomation.SUPPORTED_IDES)}")
            return {"error": "Auto mode not supported"}
        
        if self.mode == 'auto':
            self.prepare_auto_mode(ide_name)
        
        steps = self.config.steps
        if single_step:
            matching_steps = [s for s in steps if s.step_id == single_step]
            if not matching_steps:
                print(f"ERROR: Step '{single_step}' not found")
                return {"error": f"Step not found: {single_step}"}
            steps_to_run = [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "prompt_template": s.prompt_generator,
                    "validation": s.validator
                }
                for s in matching_steps
            ]
        elif start_from:
            start_idx = next((i for i, s in enumerate(steps) if s.step_id == start_from), None)
            if start_idx is None:
                print(f"ERROR: Step '{start_from}' not found")
                return {"error": f"Step not found: {start_from}"}
            steps_to_run = [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "prompt_template": s.prompt_generator,
                    "validation": s.validator
                }
                for s in steps[start_idx:]
            ]
        else:
            steps_to_run = [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "prompt_template": s.prompt_generator,
                    "validation": s.validator
                }
                for s in steps
            ]
        
        results = []
        
        for i, step in enumerate(steps_to_run):
            print(f"\n{'=' * 80}")
            print(f"Running Step {i+1}/{len(steps_to_run)}: {step['step_id']}")
            print(f"{'=' * 80}")
            
            result = self.run_step(step, ide_name)
            results.append(result)
            
            if not result["passed"]:
                print(f"\n✗ Step {step['step_id']} failed. Stopping.")
                break
        
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        for result in results:
            status = "✓ PASSED" if result["passed"] else "✗ FAILED"
            print(f"{result['step_id']}: {status}")
        
        passed_count = sum(1 for r in results if r["passed"])
        print(f"\nTotal: {passed_count}/{len(results)} steps passed")
        print(f"{'=' * 80}")
        
        return {
            "total_steps": len(results),
            "passed_steps": passed_count,
            "results": results
        }


class IntegrationTestHarness(BaseTestHarness):
    """Test harness for end-to-end integration testing."""
    
    SOLUTION_FILENAME = "integration_solution.py"
    MARKER_LINE = "### WRITE YOUR CODE BELOW. DO NOT ERASE THIS LINE OR ANYTHING ABOVE###"
    
    def __init__(self, config: MethodConfig, mode: str = 'manual'):
        super().__init__(config, mode)
        self.results_dir = self.results_base_dir / f"{config.method_name}_integration"
        
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_isolation_files(self, workspace_dir: Path) -> None:
        """Create ignore files to prevent AI from accessing test framework code."""
        cursorignore_content = """# Integration test workspace isolation
# Prevent access to test framework code and solutions
../../methods/
../methods/
methods/
../../test_framework/
../test_framework/
test_framework/
../../harness*.py
../harness*.py
../../actuarial_*.py
../actuarial_*.py
../../test_data/*/sample_solution.py
../test_data/*/sample_solution.py
../../test_data/*/step_*_starter_code.py
../test_data/*/step_*_starter_code.py
../../test_data/*/ground_truth.json
../test_data/*/ground_truth.json
../../ide_results/
../ide_results/
ide_results/
"""
        
        cursorignore_path = workspace_dir / ".cursorignore"
        WorkspaceManager.write_file(cursorignore_path, cursorignore_content)
        
        clinerules_content = """# Integration test workspace isolation
# Do not read test framework or methods directories
Do not read any files in the methods/ directory (test framework code)
Do not read any files in the test_framework/ directory
Do not read sample_solution.py files (these are answer keys)
Do not read step_*_starter_code.py files (these are for unit tests)
Do not read ground_truth.json files (these are answer keys)
Do not read files in ide_results/ directory
Only use CSV data files in test_data/ directories
Work ONLY in this directory (the integration test workspace)
"""
        
        clinerules_path = workspace_dir / ".clinerules"
        WorkspaceManager.write_file(clinerules_path, clinerules_content)
        
        aiderignore_content = """# Integration test workspace isolation
../../methods/
../methods/
methods/
../../test_framework/
../test_framework/
test_framework/
../../test_data/*/sample_solution.py
../test_data/*/sample_solution.py
../../test_data/*/step_*_starter_code.py
../test_data/*/step_*_starter_code.py
../../test_data/*/ground_truth.json
../test_data/*/ground_truth.json
../../ide_results/
../ide_results/
ide_results/
"""
        
        aiderignore_path = workspace_dir / ".aiderignore"
        WorkspaceManager.write_file(aiderignore_path, aiderignore_content)
    
    def _create_starter_file(self) -> str:
        """Create the starter file with imports and data paths."""
        csv_files = self.config.get_data_files()
        
        lines = []
        lines.append("import pandas as pd")
        lines.append("import numpy as np")
        lines.append("import chainladder as cl")
        lines.append("from pathlib import Path")
        lines.append("")
        lines.append("# Data file paths")
        for data_file in csv_files:
            abs_path = data_file.resolve()
            file_name = data_file.name.lower()
            
            if 'closed_with_pay' in file_name or 'cwp' in file_name:
                lines.append(f"cwp_count_data_path = r'{abs_path}'")
            elif 'reported_claim_count' in file_name:
                lines.append(f"reported_count_data_path = r'{abs_path}'")
            elif 'reported_claims_triangle' in file_name:
                lines.append(f"reported_claims_data_path = r'{abs_path}'")
            elif 'triangle' in file_name and 'claims' in file_name:
                lines.append(f"triangle_data_path = r'{abs_path}'")
            elif 'premium' in file_name:
                lines.append(f"premium_data_path = r'{abs_path}'")
            elif 'claim' in file_name and 'ratio' in file_name:
                lines.append(f"claim_ratio_data_path = r'{abs_path}'")
            elif 'rate' in file_name and 'change' in file_name:
                lines.append(f"rate_changes_data_path = r'{abs_path}'")
            else:
                var_name = data_file.stem.lower().replace('-', '_').replace(' ', '_') + '_data_path'
                lines.append(f"{var_name} = r'{abs_path}'")
        lines.append("")
        lines.append(self.MARKER_LINE)
        lines.append("")
        
        return "\n".join(lines)
    
    def run(self, ide_name: str) -> Dict[str, Any]:
        """Run the complete integration test."""
        print(f"\nActuarial Integration Test - {self.config.display_name}")
        print(f"IDE: {ide_name}")
        print(f"Mode: {self.mode}")
        print("=" * 80)
        
        if self.mode == 'auto' and not self.is_auto_mode_supported(ide_name):
            print(f"ERROR: Auto mode is not supported for '{ide_name}'.")
            print(f"Auto mode is only available for: {', '.join(IDEAutomation.SUPPORTED_IDES)}")
            return {"error": "Auto mode not supported"}
        
        if self.mode == 'auto':
            self.prepare_auto_mode(ide_name)
        
        workspace_dir = self.results_dir
        WorkspaceManager.create_workspace(workspace_dir, clean=True)
        
        self._create_isolation_files(workspace_dir)
        
        starter_content = self._create_starter_file()
        solution_path = workspace_dir / self.SOLUTION_FILENAME
        WorkspaceManager.write_file(solution_path, starter_content)
        
        if self.config.integration_prompt_generator:
            base_prompt = self.config.integration_prompt_generator()
            
            workspace_info = f"\nYour workspace directory: {workspace_dir.absolute()}\n"
            workspace_info += f"The file you need to edit: {solution_path.absolute()}\n"
            
            prompt_lines = base_prompt.split('\n')
            title_line = prompt_lines[0]
            rest_of_prompt = '\n'.join(prompt_lines[1:])
            
            prompt = title_line + '\n' + workspace_info + rest_of_prompt
        else:
            raise ValueError("Integration prompt generator not configured")
        
        PromptHandler.display_instructions(
            workspace_dir,
            self.SOLUTION_FILENAME,
            ide_name,
            self.mode,
            True
        )
        
        self.deliver_prompt(prompt, ide_name)
        self.wait_for_solution(workspace_dir, self.SOLUTION_FILENAME)
        
        print("\n--- Validating Solution ---")
        
        if self.config.integration_validator:
            validation_result = self.config.integration_validator(workspace_dir)
        else:
            raise ValueError("Integration validator not configured")
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        if validation_result["passed"]:
            print("✓ TEST PASSED")
            if "total_ultimate" in validation_result:
                print(f"\nTotal Ultimate: {validation_result['total_ultimate']:,.2f}")
                print(f"Expected:       {validation_result['expected_ultimate']:,.2f}")
            if "total_ibnr" in validation_result:
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
        
        def convert_to_serializable(obj):
            """Convert numpy types to Python native types for JSON serialization."""
            import numpy as np
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return obj
        
        result_summary = {
            "method": self.config.method_name,
            "ide": ide_name,
            "mode": self.mode,
            "passed": bool(validation_result["passed"]),
            "validation_details": convert_to_serializable(validation_result),
            "workspace": str(workspace_dir.absolute())
        }
        
        results_path = self.results_dir / "integration_test_results.json"
        with open(results_path, 'w') as f:
            json.dump(result_summary, f, indent=2)
        
        print(f"Results saved to: {results_path}")
        
        return result_summary

