#!/usr/bin/env python3
"""
Unified Test Harness for Actuarial Methods

This is the single entry point for running unit and integration tests
on actuarial methods using AI coding assistants.

Usage:
  python run_tests.py --method friedland_xyz_dev_method --test-type unit --ide cursor --mode auto
  python run_tests.py --method friedland_xyz_dev_method --test-type integration --ide cursor --mode manual
  python run_tests.py --list-methods
  
Examples:
  python run_tests.py --method friedland_xyz_dev_method --test-type unit --ide cursor --mode auto
  python run_tests.py --method friedland_xyz_dev_method --test-type unit --ide cursor --mode manual --step step_3
  python run_tests.py --method friedland_xyz_dev_method --test-type integration --ide cursor --mode auto
"""

import argparse
import sys
from pathlib import Path

from test_framework import MethodRegistry, UnitTestHarness, IntegrationTestHarness


def list_methods():
    """List all available methods."""
    MethodRegistry.discover_methods()
    methods = MethodRegistry.list_methods()
    
    if not methods:
        print("No methods found. Please check the methods/ directory.")
        return
    
    print("Available methods:")
    for method_name in sorted(methods):
        config = MethodRegistry.get(method_name)
        print(f"  - {method_name}: {config.display_name}")


def run_unit_tests(method_name: str, ide_name: str, mode: str, start_from: str = None, single_step: str = None):
    """Run unit tests for a method."""
    MethodRegistry.discover_methods()
    
    try:
        config = MethodRegistry.get(method_name)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable methods:")
        for name in MethodRegistry.list_methods():
            print(f"  - {name}")
        return 1
    
    harness = UnitTestHarness(config, mode=mode)
    harness.run(ide_name, start_from=start_from, single_step=single_step)
    return 0


def run_integration_tests(method_name: str, ide_name: str, mode: str):
    """Run integration tests for a method."""
    MethodRegistry.discover_methods()
    
    try:
        config = MethodRegistry.get(method_name)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable methods:")
        for name in MethodRegistry.list_methods():
            print(f"  - {name}")
        return 1
    
    harness = IntegrationTestHarness(config, mode=mode)
    harness.run(ide_name)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Unified Test Harness for Actuarial Methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--method', type=str,
                        help='Actuarial method to test (e.g., friedland_xyz_dev_method)')
    parser.add_argument('--test-type', choices=['unit', 'integration'],
                        help='Type of test to run')
    parser.add_argument('--ide', type=str,
                        help='IDE to use (e.g., cursor, continue, cline)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation (default: manual)')
    parser.add_argument('--start-from', type=str,
                        help='Start from specific step ID (unit tests only)')
    parser.add_argument('--step', type=str,
                        help='Run only specific step ID (unit tests only)')
    parser.add_argument('--list-methods', action='store_true',
                        help='List all available methods and exit')
    
    args = parser.parse_args()
    
    if args.list_methods:
        list_methods()
        return 0
    
    if not args.method:
        parser.error("--method is required (or use --list-methods)")
    
    if not args.test_type:
        parser.error("--test-type is required")
    
    if not args.ide:
        parser.error("--ide is required")
    
    if args.test_type == 'unit':
        return run_unit_tests(
            args.method,
            args.ide,
            args.mode,
            start_from=args.start_from,
            single_step=args.step
        )
    elif args.test_type == 'integration':
        if args.start_from or args.step:
            print("Warning: --start-from and --step are ignored for integration tests")
        return run_integration_tests(args.method, args.ide, args.mode)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

