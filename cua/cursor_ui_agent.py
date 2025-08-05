"""
Main Cursor UI Agent (CUA) orchestrator
Combines visual detection and automation for complete Cursor interaction
"""
import time
from typing import Optional, Tuple

from .detection.visual_detector import VisualDetector
from .actions.automation import AutomationController
from .config.settings import CUAConfig


class CursorUIAgent:
    """
    Main CUA class that orchestrates the complete interaction workflow
    """
    
    def __init__(self):
        self.config = CUAConfig()
        self.detector = VisualDetector()
        self.automation = AutomationController()
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate that all required components are properly configured"""
        try:
            self.config.validate()
            print("✓ CUA configuration validated")
        except ValueError as e:
            print(f"✗ Configuration error: {e}")
            raise
    
    def find_and_click_input(self) -> bool:
        """
        Find chat input box and click on it
        Returns: True if successful, False otherwise
        """
        print("\n=== DETECTING INPUT BOX ===")
        
        # Detect input box location
        coordinates = self.detector.detect_chat_input()
        if not coordinates:
            print("✗ Could not detect chat input box")
            return False
        
        center_x, center_y = coordinates
        
        # Click on the detected location
        print("\n=== CLICKING INPUT BOX ===")
        success = self.automation.move_and_click(center_x, center_y)
        
        if success:
            print("✓ Input box clicked successfully")
        else:
            print("✗ Failed to click input box")
        
        return success
    
    def run_phase1_test(self) -> bool:
        """
        Run Phase 1: Basic functionality test
        Returns: True if successful, False otherwise
        """
        print("\n=== PHASE 1: BASIC TEST ===")
        
        # Find and click input box
        if not self.find_and_click_input():
            return False
        
        # Submit basic test prompt
        print("\n=== SUBMITTING PHASE 1 PROMPT ===")
        success = self.automation.submit_prompt(self.config.PHASE1_PROMPT)
        
        if success:
            print("✓ Phase 1 completed successfully")
            self.automation.wait_for_response()
        else:
            print("✗ Phase 1 failed")
        
        return success
    
    def run_phase2_test(self) -> bool:
        """
        Run Phase 2: Real-world prompt test
        Returns: True if successful, False otherwise
        """
        print("\n=== PHASE 2: REAL-WORLD TEST ===")
        
        # Re-detect input box (it might have moved)
        print("\n=== RE-DETECTING INPUT BOX ===")
        if not self.find_and_click_input():
            return False
        
        # Clear any previous input and submit real prompt
        print("\n=== SUBMITTING PHASE 2 PROMPT ===")
        success = self.automation.submit_prompt(
            self.config.PHASE2_PROMPT, 
            clear_first=True
        )
        
        if success:
            print("✓ Phase 2 completed successfully")
            self.automation.wait_for_response()
        else:
            print("✗ Phase 2 failed")
        
        return success
    
    def start_new_chat_session(self) -> bool:
        """
        Start a new chat session in Cursor
        Returns: True if successful, False otherwise
        """
        print("\n=== STARTING NEW CHAT ===")
        return self.automation.new_chat()
    
    def run_complete_test(self) -> bool:
        """
        Run the complete two-phase test workflow
        Returns: True if both phases successful, False otherwise
        """
        print("=== CURSOR UI AGENT STARTING ===")
        print(f"Phase 1 prompt: {self.config.PHASE1_PROMPT[:50]}...")
        print(f"Phase 2 prompt: {self.config.PHASE2_PROMPT[:50]}...")
        
        try:
            # Phase 1: Basic test
            if not self.run_phase1_test():
                print("Phase 1 failed - stopping execution")
                return False
            
            print("\n=== WAITING BETWEEN PHASES ===")
            self.automation.wait_for_response(self.config.PHASE_WAIT_TIME)
            
            # Phase 2: Real-world test
            if not self.run_phase2_test():
                print("Phase 2 failed")
                return False
            
            print("\n=== ALL PHASES COMPLETED SUCCESSFULLY ===")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹=== EXECUTION STOPPED BY USER ===")
            return False
        except Exception as e:
            print(f"\n=== UNEXPECTED ERROR: {e} ===")
            return False
    
    def send_custom_prompt(self, prompt: str, new_chat: bool = False) -> bool:
        """
        Send a custom prompt to Cursor
        
        Args:
            prompt: The prompt text to send
            new_chat: Whether to start a new chat first
            
        Returns: True if successful, False otherwise
        """
        print(f"\n=== SENDING CUSTOM PROMPT ===")
        print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        try:
            # Start new chat if requested
            if new_chat:
                if not self.start_new_chat_session():
                    return False
            
            # Find and click input box
            if not self.find_and_click_input():
                return False
            
            # Submit the prompt
            success = self.automation.submit_prompt(prompt, clear_first=True)
            
            if success:
                print("✓ Custom prompt sent successfully")
                self.automation.wait_for_response()
            else:
                print("✗ Failed to send custom prompt")
            
            return success
            
        except Exception as e:
            print(f"✗ Custom prompt failed: {e}")
            return False
    
    def interactive_mode(self):
        """
        Interactive mode for testing CUA functionality
        """
        print("\n=== INTERACTIVE CUA MODE ===")
        print("Commands:")
        print("  1 - Run Phase 1 test")
        print("  2 - Run Phase 2 test") 
        print("  full - Run complete two-phase test")
        print("  new - Start new chat")
        print("  custom - Send custom prompt")
        print("  quit - Exit")
        
        while True:
            try:
                command = input("\nCUA> ").strip().lower()
                
                if command == "quit" or command == "q":
                    break
                elif command == "1":
                    self.run_phase1_test()
                elif command == "2":
                    self.run_phase2_test()
                elif command == "full":
                    self.run_complete_test()
                elif command == "new":
                    self.start_new_chat_session()
                elif command == "custom":
                    prompt = input("Enter your prompt: ")
                    new_chat = input("Start new chat? (y/n): ").lower() == 'y'
                    self.send_custom_prompt(prompt, new_chat)
                else:
                    print("Unknown command. Try 'full', '1', '2', 'new', 'custom', or 'quit'")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n=== CUA SESSION ENDED ===")


def main():
    """Main entry point for CUA"""
    try:
        cua = CursorUIAgent()
        
        # Run interactive mode by default
        cua.interactive_mode()
        
    except Exception as e:
        print(f"Failed to initialize CUA: {e}")
        return False


if __name__ == "__main__":
    main()