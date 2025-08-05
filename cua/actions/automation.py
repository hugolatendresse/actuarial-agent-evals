"""
Action execution module for CUA - handles mouse and keyboard automation
"""
import time
import pyautogui
import pyperclip
from typing import Tuple, Optional

from ..config.settings import CUAConfig


class AutomationController:
    """Handles mouse movement, clicking, and keyboard input"""
    
    def __init__(self):
        self.config = CUAConfig()
        # Configure pyautogui settings
        pyautogui.FAILSAFE = True  # Move mouse to top-left to abort
        pyautogui.PAUSE = self.config.CLICK_DELAY
    
    def move_and_click(self, x: int, y: int) -> bool:
        """
        Move mouse to coordinates and click
        Returns: True if successful, False otherwise
        """
        try:
            print(f"Moving mouse to ({x}, {y})")
            
            # Move mouse to target position
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(self.config.CLICK_DELAY)
            
            # Click at the position
            pyautogui.click(x, y)
            time.sleep(self.config.CLICK_DELAY)
            
            print("✓ Click successful")
            return True
            
        except Exception as e:
            print(f"✗ Click failed: {e}")
            return False
    
    def paste_text(self, text: str) -> bool:
        """
        Paste text using clipboard (more reliable than typing)
        Returns: True if successful, False otherwise
        """
        try:
            print(f"Pasting text: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Copy text to clipboard
            pyperclip.copy(text)
            time.sleep(self.config.TYPE_DELAY)
            
            # Paste using Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(self.config.TYPE_DELAY)
            
            print("✓ Text pasted successfully")
            return True
            
        except Exception as e:
            print(f"✗ Paste failed: {e}")
            return False
    
    def press_enter(self) -> bool:
        """
        Press Enter key to submit
        Returns: True if successful, False otherwise
        """
        try:
            print("⏎ Pressing Enter")
            pyautogui.press('enter')
            time.sleep(self.config.TYPE_DELAY)
            print("✓ Enter pressed successfully")
            return True
            
        except Exception as e:
            print(f"✗ Enter press failed: {e}")
            return False
    
    def clear_input(self) -> bool:
        """
        Clear input field by selecting all and deleting
        Returns: True if successful, False otherwise
        """
        try:
            print("Clearing input field")
            
            # Select all text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(self.config.TYPE_DELAY)
            
            # Delete selected text
            pyautogui.press('delete')
            time.sleep(self.config.TYPE_DELAY)
            
            print("✓ Input cleared successfully")
            return True
            
        except Exception as e:
            print(f"✗ Clear input failed: {e}")
            return False
    
    def new_chat(self) -> bool:
        """
        Start a new chat using Ctrl+N
        Returns: True if successful, False otherwise
        """
        try:
            print("Starting new chat (Ctrl+N)")
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(self.config.PHASE_WAIT_TIME)  # Wait for new chat to load
            print("✓ New chat started successfully")
            return True
            
        except Exception as e:
            print(f"✗ New chat failed: {e}")
            return False
    
    def submit_prompt(self, prompt: str, clear_first: bool = False) -> bool:
        """
        Complete prompt submission workflow
        Returns: True if successful, False otherwise
        """
        try:
            # Clear input if requested
            if clear_first:
                if not self.clear_input():
                    return False
            
            # Paste the prompt
            if not self.paste_text(prompt):
                return False
            
            # Submit with Enter
            if not self.press_enter():
                return False
            
            print("✓ Prompt submitted successfully")
            return True
            
        except Exception as e:
            print(f"✗ Prompt submission failed: {e}")
            return False
    
    def wait_for_response(self, seconds: float = None) -> None:
        """Wait for AI response with optional custom duration"""
        wait_time = seconds or self.config.PHASE_WAIT_TIME
        print(f"⏳ Waiting {wait_time} seconds for response...")
        time.sleep(wait_time)
    
    def focus_cursor_window(self) -> bool:
        """
        Attempt to focus the Cursor window
        Returns: True if successful, False otherwise
        """
        try:
            # This is platform-specific - you might need to adjust
            # On macOS, you could use AppleScript or similar
            # For now, we'll use a simple click approach
            print("Attempting to focus Cursor window")
            
            # Click somewhere safe on screen to ensure focus
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"✗ Focus failed: {e}")
            return False