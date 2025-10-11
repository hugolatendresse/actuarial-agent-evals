"""
Actuarial Integration Test Harness

Tests the AI's ability to perform a complete chainladder analysis in one shot,
rather than step-by-step. This tests end-to-end competency.

Usage:
  python actuarial_integration_test.py --method friedland_xyz_dev_method --ide cursor --mode auto
  python actuarial_integration_test.py --method friedland_xyz_dev_method --ide cursor --mode manual
"""

import argparse
import sys
from test_framework import MethodRegistry, IntegrationTestHarness


def main():
    parser = argparse.ArgumentParser(description='Actuarial Integration Test')
    parser.add_argument('--method', type=str, required=True,
                        help='Actuarial method to test (e.g., friedland_xyz_dev_method)')
    parser.add_argument('--ide', type=str, required=True,
                        help='IDE to use (e.g., cursor, continue, cline)')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual',
                        help='Mode of operation')
    
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
    
    harness = IntegrationTestHarness(config, mode=args.mode)
    harness.run(args.ide)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
