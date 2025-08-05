"""
Integration module for connecting CUA with the existing harness system
Automates the manual Cursor interactions in harness.py
"""
import time
from typing import Optional, List, Dict, Any

from ..cursor_ui_agent import CursorUIAgent
from ..config.settings import CUAConfig


class HarnessIntegrator:
    """
    Integrates CUA with the existing actuarial AI harness system
    Replaces manual Cursor interactions with automated ones
    """
    
    def __init__(self, enable_automation: bool = True):
        """
        Initialize the harness integrator
        
        Args:
            enable_automation: If False, falls back to manual mode
        """
        self.enable_automation = enable_automation
        self.cua = None
        
        if enable_automation:
            try:
                self.cua = CursorUIAgent()
                print("✓ CUA automation enabled")
            except Exception as e:
                print(f"⚠ CUA automation failed to initialize: {e}")
                print("⚠ Falling back to manual mode")
                self.enable_automation = False
    
    def automated_cursor_interaction(self, prompt: str, new_chat: bool = True) -> bool:
        """
        Automated replacement for manual Cursor interaction
        
        This replaces the manual steps in harness.py:
        - click into cursor
        - ctrl+N to start new chat  
        - ctrl+V to paste prompt
        - enter to submit
        
        Args:
            prompt: The prompt to send to Cursor
            new_chat: Whether to start a new chat session
            
        Returns: True if successful, False if failed
        """
        if not self.enable_automation or not self.cua:
            return self._manual_fallback(prompt)
        
        try:
            print(f"\n=== AUTOMATED CURSOR INTERACTION ===")
            print(f"Prompt length: {len(prompt)} characters")
            print(f"New chat: {new_chat}")
            
            # Send the prompt using CUA
            success = self.cua.send_custom_prompt(prompt, new_chat=new_chat)
            
            if success:
                print("✓ Automated interaction completed successfully")
                return True
            else:
                print("⚠ Automated interaction failed, trying manual fallback")
                return self._manual_fallback(prompt)
                
        except Exception as e:
            print(f"✗ Automated interaction error: {e}")
            print("⚠ Falling back to manual mode")
            return self._manual_fallback(prompt)
    
    def _manual_fallback(self, prompt: str) -> bool:
        """
        Fallback to original manual interaction method
        Uses pyperclip to put prompt in clipboard and waits for user
        """
        import pyperclip
        
        print(f"\n👤 === MANUAL CURSOR INTERACTION ===")
        print("CUA automation not available - using manual mode")
        print("\nPrompt has been copied to clipboard.")
        print("Please:")
        print("1. Click into Cursor")
        print("2. Press Ctrl+N to start new chat")  
        print("3. Press Ctrl+V to paste the prompt")
        print("4. Press Enter to submit")
        print("5. Press any key here when done...")
        
        # Copy prompt to clipboard
        pyperclip.copy(prompt)
        
        # Wait for user to complete manual steps
        input("\nPress Enter when you've completed the manual steps...")
        
        return True
    
    def run_test_batch(self, test_prompts: List[str], delay_between_tests: float = 10.0) -> List[bool]:
        """
        Run a batch of test prompts through Cursor
        
        Args:
            test_prompts: List of prompts to test
            delay_between_tests: Seconds to wait between tests
            
        Returns: List of success/failure results
        """
        results = []
        
        print(f"\n=== RUNNING BATCH TEST ({len(test_prompts)} prompts) ===")
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i}/{len(test_prompts)} ---")
            
            # Run the test
            success = self.automated_cursor_interaction(
                prompt, 
                new_chat=True  # Always start fresh chat for each test
            )
            results.append(success)
            
            # Wait between tests (except for the last one)
            if i < len(test_prompts):
                print(f"Waiting {delay_between_tests} seconds before next test...")
                time.sleep(delay_between_tests)
        
        # Print summary
        successful = sum(results)
        print(f"\n=== BATCH TEST COMPLETE ===")
        print(f"Successful: {successful}/{len(test_prompts)}")
        print(f"Failed: {len(test_prompts) - successful}/{len(test_prompts)}")
        
        return results
    
    def validate_cursor_responsiveness(self) -> bool:
        """
        Quick validation that Cursor is responsive and CUA can interact with it
        
        Returns: True if Cursor responds properly, False otherwise
        """
        if not self.enable_automation or not self.cua:
            print("⚠ Automation not available - skipping validation")
            return True
        
        print("\n=== VALIDATING CURSOR RESPONSIVENESS ===")
        
        # Try to detect input box without clicking
        coordinates = self.cua.detector.detect_chat_input()
        if not coordinates:
            print("✗ Cannot detect Cursor chat input - is Cursor open and visible?")
            return False
        
        print("✓ Cursor input box detected successfully")
        
        # Optionally run a quick test prompt
        test_prompt = "Hello, this is a test message."
        success = self.cua.send_custom_prompt(test_prompt, new_chat=True)
        
        if success:
            print("✓ Cursor responsiveness validation passed")
        else:
            print("✗ Cursor responsiveness validation failed")
        
        return success
    
    def get_automation_status(self) -> Dict[str, Any]:
        """
        Get current status of automation system
        
        Returns: Dictionary with status information
        """
        status = {
            "automation_enabled": self.enable_automation,
            "cua_initialized": self.cua is not None,
            "config_valid": False,
            "detection_available": False,
            "automation_available": False
        }
        
        if self.cua:
            try:
                # Check if config is valid
                self.cua.config.validate()
                status["config_valid"] = True
                
                # Check if detection is available
                if self.cua.detector.processor and self.cua.detector.model:
                    status["detection_available"] = True
                
                # Check if automation is available
                status["automation_available"] = True
                
            except Exception as e:
                status["error"] = str(e)
        
        return status
    
    def print_status(self):
        """Print current automation status"""
        status = self.get_automation_status()
        
        print("\n=== CUA INTEGRATION STATUS ===")
        print(f"Automation Enabled: {'✓' if status['automation_enabled'] else '✗'}")
        print(f"CUA Initialized: {'✓' if status['cua_initialized'] else '✗'}")
        print(f"Config Valid: {'✓' if status['config_valid'] else '✗'}")
        print(f"Detection Available: {'✓' if status['detection_available'] else '✗'}")
        print(f"Automation Available: {'✓' if status['automation_available'] else '✗'}")
        
        if 'error' in status:
            print(f"Error: {status['error']}")
        
        if not status['automation_enabled']:
            print("\nNote: Manual fallback mode will be used")


# Convenience function for easy import in harness.py
def create_harness_integrator(enable_automation: bool = True) -> HarnessIntegrator:
    """
    Factory function to create a HarnessIntegrator
    
    Args:
        enable_automation: Whether to enable CUA automation
        
    Returns: Configured HarnessIntegrator instance
    """
    return HarnessIntegrator(enable_automation=enable_automation)