#!/usr/bin/env python3
"""
Run All Integration Tests

Runs integration tests for all actuarial methods using AI coding assistants.

Usage:
  Note the "--ide" argument below specifies which AI bot to paste into, NOT the ide we are using.
  python run_tests.py --ide cline --mode auto
  python run_tests.py --ide cursor --mode manual
"""

import argparse
import sys
import json
import time
from pathlib import Path
from test_framework import MethodRegistry, IntegrationTestHarness


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
        print(f"{result['method']:<{header_width}}  {status:<10}  {elapsed:<10}")
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    percentage = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print("-" * 80)
    print(f"\nTotal: {passed_count}/{total_count} passed ({percentage:.1f}%)")
    print(f"{'=' * 80}")
    
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
        "results": results
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\nSummary saved to: {summary_path}")
    
    return 0 if passed_count == total_count else 1


def main():
    parser = argparse.ArgumentParser(
        description='Run all integration tests for actuarial methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--ide', type=str, required=True,
                        help='IDE to use (e.g., cursor, cline, continue)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation (default: manual)')
    
    args = parser.parse_args()
    
    return run_all_integration_tests(args.ide, args.mode)


if __name__ == '__main__':
    sys.exit(main())
