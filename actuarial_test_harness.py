"""
Actuarial Test Harness for Sequential Method Testing

This harness tests actuarial methods step-by-step, building cumulative code
and validating each intermediate result.

Usage:
  python actuarial_test_harness.py --method friedland_xyz_fs1_method --ide cline --mode auto
  python actuarial_test_harness.py --method friedland_xyz_fs1_method --ide cline --mode manual
  python actuarial_test_harness.py --method friedland_xyz_fs1_method --ide cline --step step_2
"""

import argparse
import sys
from test_framework import MethodRegistry, UnitTestHarness


def main():
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
    
    MethodRegistry.discover_methods()
    
    try:
        config = MethodRegistry.get(args.method)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable methods:")
        for name in MethodRegistry.list_methods():
            print(f"  - {name}")
        return 1
    
    harness = UnitTestHarness(config, mode=args.mode)
    harness.run(args.ide, start_from=args.start_from, single_step=args.step)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
