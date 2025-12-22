#!/usr/bin/env python3
"""
Run All Integration or Unit Tests

Runs integration or unit tests for all actuarial methods using AI coding assistants.

Usage:
  python launch_all_tests.py --ide cline --mode auto --test-type integration
  python launch_all_tests.py --ide cursor --mode manual --test-type unit
"""

import argparse
import sys
import json
import time
from pathlib import Path
from test_framework import MethodRegistry, IntegrationTestHarness, UnitTestHarness


def run_all_unit_tests(ide_name: str, mode: str):
    """Run unit tests for all registered methods."""
    MethodRegistry.discover_methods()
    all_methods = MethodRegistry.list_methods()

    if not all_methods:
        print("No methods found in registry.")
        return 1

    print("\nRunning unit tests for ALL methods")
    print(f"IDE: {ide_name}")
    print(f"Mode: {mode}")
    print(f"Total methods: {len(all_methods)}")
    print("=" * 80)

    results = []
    first_test = True

    for i, method_name in enumerate(all_methods, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(all_methods)}: {method_name}")
        print(f"{'=' * 80}")

        start_time = time.time()

        try:
            config = MethodRegistry.get(method_name)
            harness = UnitTestHarness(config, mode=mode)

            if not first_test:
                harness.first_question = False

            result = harness.run(ide_name)

            if first_test:
                first_test = False

            elapsed_time = time.time() - start_time

            total_steps = result.get("total_steps", 0)
            passed_steps = result.get("passed_steps", 0)

            results.append({
                "method": method_name,
                "passed": passed_steps == total_steps and total_steps > 0,
                "total_steps": total_steps,
                "passed_steps": passed_steps,
                "error": result.get("error"),
                "elapsed_time": elapsed_time,
                "result_details": result
            })

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\nERROR: Test for {method_name} crashed: {e}")
            results.append({
                "method": method_name,
                "passed": False,
                "total_steps": 0,
                "passed_steps": 0,
                "error": str(e),
                "elapsed_time": elapsed_time,
                "result_details": None
            })

            if first_test:
                first_test = False

    print(f"\n\n{'=' * 80}")
    print("ALL UNIT TESTS SUMMARY")
    print(f"{'=' * 80}")

    max_method_len = max(len(r["method"]) for r in results)
    header_width = max(max_method_len, 30)

    print(f"{'Method':<{header_width}}  {'Status':<10}  {'Steps':<12}  {'Time (s)':<10}")
    print("-" * 80)

    for result in results:
        status = "PASSED" if result["passed"] else "FAILED"
        steps = f"{result['passed_steps']}/{result['total_steps']}"
        elapsed = f"{result['elapsed_time']:.1f}"
        print(
            f"{result['method']:<{header_width}}  {status:<10}  {steps:<12}  {elapsed:<10}")

    total_steps_passed = sum(r.get('passed_steps', 0) for r in results)
    total_steps_count = sum(r.get('total_steps', 0) for r in results)
    methods_passed = sum(1 for r in results if r["passed"])
    methods_count = len(results)
    percentage = (total_steps_passed / total_steps_count *
                  100) if total_steps_count > 0 else 0

    print("-" * 80)
    print(
        f"\nTotal: {total_steps_passed}/{total_steps_count} steps passed ({percentage:.1f}%)")
    print(f"Methods: {methods_passed}/{methods_count} methods fully passed")

    failed_results = [r for r in results if not r["passed"]]
    if failed_results:
        print(f"\n{'=' * 80}")
        print("FAILED TESTS DETAILS")
        print(f"{'=' * 80}")

        for result in failed_results:
            print(f"\n{result['method']}:")

            if result.get("result_details") and "results" in result["result_details"]:
                step_results = result["result_details"]["results"]
                for step_result in step_results:
                    if not step_result.get("passed", True):
                        print(
                            f"  Step {step_result.get('step_id', 'unknown')}: FAILED")
                        if "validation_result" in step_result:
                            val_result = step_result["validation_result"]
                            if "error" in val_result:
                                print(f"    Error: {val_result['error']}")
                            if "errors" in val_result and val_result["errors"]:
                                for error in val_result["errors"]:
                                    print(f"    - {error}")
            elif result.get("error"):
                print(f"  Error: {result['error']}")

    print(f"\n{'=' * 80}")

    def convert_to_serializable(obj):
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

    results_dir = Path("ide_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    summary_path = results_dir / "all_unit_tests_summary.json"

    summary_data = {
        "ide": ide_name,
        "mode": mode,
        "total_tests": total_count,
        "passed_tests": passed_count,
        "failed_tests": total_count - passed_count,
        "pass_percentage": percentage,
        "results": convert_to_serializable(results)
    }

    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"\nSummary saved to: {summary_path}")

    return 0 if passed_count == total_count else 1


def run_all_integration_tests(ide_name: str, mode: str):
    """Run integration tests for all registered methods."""
    MethodRegistry.discover_methods()
    all_methods = MethodRegistry.list_methods()

    if not all_methods:
        print("No methods found in registry.")
        return 1

    print("\nRunning integration tests for ALL methods")
    print(f"IDE: {ide_name}")
    print(f"Mode: {mode}")
    print(f"Total methods: {len(all_methods)}")
    print("=" * 80)

    results = []
    first_test = True

    for i, method_name in enumerate(all_methods, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(all_methods)}: {method_name}")
        print(f"{'=' * 80}")

        start_time = time.time()

        try:
            config = MethodRegistry.get(method_name)
            harness = IntegrationTestHarness(config, mode=mode)

            if not first_test:
                harness.first_question = False

            result = harness.run(ide_name)

            if first_test:
                first_test = False

            elapsed_time = time.time() - start_time

            results.append({
                "method": method_name,
                "passed": result.get("passed", False),
                "error": result.get("error"),
                "elapsed_time": elapsed_time,
                "result_details": result
            })

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\nERROR: Test for {method_name} crashed: {e}")
            results.append({
                "method": method_name,
                "passed": False,
                "error": str(e),
                "elapsed_time": elapsed_time,
                "result_details": None
            })

            if first_test:
                first_test = False

    print(f"\n\n{'=' * 80}")
    print("ALL INTEGRATION TESTS SUMMARY")
    print(f"{'=' * 80}")

    max_method_len = max(len(r["method"]) for r in results)
    header_width = max(max_method_len, 30)

    print(f"{'Method':<{header_width}}  {'Status':<10}  {'Time (s)':<10}")
    print("-" * 80)

    for result in results:
        status = "PASSED" if result["passed"] else "FAILED"
        elapsed = f"{result['elapsed_time']:.1f}"
        print(
            f"{result['method']:<{header_width}}  {status:<10}  {elapsed:<10}")

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    percentage = (passed_count / total_count * 100) if total_count > 0 else 0

    print("-" * 80)
    print(f"\nTotal: {passed_count}/{total_count} passed ({percentage:.1f}%)")

    # Print detailed failures
    failed_results = [r for r in results if not r["passed"]]
    if failed_results:
        print(f"\n{'=' * 80}")
        print("FAILED TESTS DETAILS")
        print(f"{'=' * 80}")

        for result in failed_results:
            print(f"\n{result['method']}:")

            # Extract validation errors from result_details
            if result.get("result_details") and "validation_errors" in result["result_details"]:
                errors = result["result_details"]["validation_errors"]
                for error in errors:
                    print(f"  {error}")
            elif result.get("error"):
                print(f"  Error: {result['error']}")

    print(f"\n{'=' * 80}")

    def convert_to_serializable(obj):
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

    results_dir = Path("ide_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    summary_path = results_dir / "all_integration_tests_summary.json"

    summary_data = {
        "ide": ide_name,
        "mode": mode,
        "total_tests": total_count,
        "passed_tests": passed_count,
        "failed_tests": total_count - passed_count,
        "pass_percentage": percentage,
        "results": convert_to_serializable(results)
    }

    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"\nSummary saved to: {summary_path}")

    return 0 if passed_count == total_count else 1


def main():
    parser = argparse.ArgumentParser(
        description='Run all integration or unit tests for actuarial methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--ide', type=str, required=True,
                        help='IDE to use (e.g., cursor, cline, continue)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation (default: manual)')
    parser.add_argument('--test-type', choices=['integration', 'unit'], required=True,
                        help='Type of tests to run (integration or unit)')

    args = parser.parse_args()

    if args.test_type == 'integration':
        return run_all_integration_tests(args.ide, args.mode)
    elif args.test_type == 'unit':
        return run_all_unit_tests(args.ide, args.mode)
    else:
        print(f"Unknown test type: {args.test_type}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
