#!/usr/bin/env python3
"""
Test script for Cursor UI Agent (CUA)
Run this to test CUA functionality before integrating with harness
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cua import CursorUIAgent, create_harness_integrator


def test_basic_cua():
    """Test basic CUA functionality"""
    print("=== TESTING BASIC CUA FUNCTIONALITY ===")
    
    try:
        # Initialize CUA
        cua = CursorUIAgent()
        print("✓ CUA initialized successfully")
        
        # Test interactive mode
        print("\nStarting interactive mode...")
        print("Try commands like 'full', '1', '2', 'custom', or 'quit'")
        cua.interactive_mode()
        
    except Exception as e:
        print(f"✗ CUA test failed: {e}")
        return False
    
    return True


def test_harness_integration():
    """Test CUA integration with harness system"""
    print("\n=== TESTING HARNESS INTEGRATION ===")
    
    try:
        # Create integrator
        integrator = create_harness_integrator(enable_automation=True)
        integrator.print_status()
        
        # Test validation
        is_responsive = integrator.validate_cursor_responsiveness()
        
        if is_responsive:
            print("✓ Cursor responsiveness validation passed")
            
            # Test a simple prompt
            test_prompt = "Write a simple 'Hello World' program in Python."
            success = integrator.automated_cursor_interaction(test_prompt, new_chat=True)
            
            if success:
                print("✓ Harness integration test successful")
                return True
            else:
                print("✗ Harness integration test failed")
                return False
        else:
            print("⚠ Cursor not responsive - check if Cursor is open and visible")
            return False
            
    except Exception as e:
        print(f"✗ Harness integration test failed: {e}")
        return False


def test_batch_operation():
    """Test batch prompt processing"""
    print("\n=== TESTING BATCH OPERATION ===")
    
    try:
        integrator = create_harness_integrator(enable_automation=True)
        
        # Sample test prompts
        test_prompts = [
            "Calculate 2 + 2",
            "Write a function that returns the current date",
            "Explain what Python is in one sentence"
        ]
        
        print(f"Running batch test with {len(test_prompts)} prompts...")
        results = integrator.run_test_batch(test_prompts, delay_between_tests=5.0)
        
        successful = sum(results)
        print(f"Batch test results: {successful}/{len(test_prompts)} successful")
        
        return successful == len(test_prompts)
        
    except Exception as e:
        print(f"✗ Batch operation test failed: {e}")
        return False


def main():
    """Main test runner"""
    print("=== CUA TEST SUITE ===")
    print("Make sure Cursor is open and visible before running tests!\n")
    
    # Ask user what to test
    print("Available tests:")
    print("1. Basic CUA functionality (interactive)")
    print("2. Harness integration")
    print("3. Batch operation")
    print("4. All tests")
    
    choice = input("\nSelect test (1-4): ").strip()
    
    if choice == "1":
        test_basic_cua()
    elif choice == "2":
        test_harness_integration()
    elif choice == "3":
        test_batch_operation()
    elif choice == "4":
        print("Running all tests...")
        test_harness_integration()
        print("\n" + "="*50)
        test_batch_operation()
        print("\n" + "="*50)
        test_basic_cua()
    else:
        print("Invalid choice")
        return
    
    print("\n🏁 === TEST SUITE COMPLETE ===")


if __name__ == "__main__":
    main()