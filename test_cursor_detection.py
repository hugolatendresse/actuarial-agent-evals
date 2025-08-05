#!/usr/bin/env python3
"""
Simple test to verify CUA can detect Cursor's chat input box
Run this while Cursor is open to test the detection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cua.detection.visual_detector import VisualDetector

def test_cursor_detection():
    """Test if CUA can detect Cursor's chat input box"""
    print("=== TESTING CURSOR DETECTION ===")
    print("Make sure Cursor is open with a chat interface visible!")
    print("")
    
    input("Press Enter when Cursor is ready...")
    
    try:
        # Initialize detector
        detector = VisualDetector()
        print("✓ Visual detector initialized")
        
        # Try to detect chat input
        print("📸 Taking screenshot and looking for chat input box...")
        coordinates = detector.detect_chat_input()
        
        if coordinates:
            x, y = coordinates
            print(f"SUCCESS! Chat input box detected at ({x}, {y})")
            print("CUA should be able to automatically click and interact with Cursor!")
            return True
        else:
            print("Could not detect chat input box")
            print("Tips:")
            print("- Make sure Cursor is open and visible")
            print("- Make sure a chat interface is visible") 
            print("- Try opening a new chat (Ctrl+N)")
            print("- Make sure the input box is not covered or obscured")
            return False
            
    except Exception as e:
        print(f"Detection failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_cursor_detection()
    
    if success:
        print("\nCUA detection test PASSED!")
        print("Your CUA is ready for automation!")
        print("\nNext steps:")
        print("1. Try: python harness.py")
        print("2. Choose automation (y) when prompted")
        print("3. Enter 'Cursor' as the IDE name")
    else:
        print("\nDetection test failed!")
        print("CUA will fall back to manual mode automatically")
        print("You can still use the harness in manual mode")