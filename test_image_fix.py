#!/usr/bin/env python3
"""
Test script to verify the image format fix for OWLv2
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_image_processing():
    """Test the image format fix"""
    print("=== TESTING IMAGE FORMAT FIX ===")
    
    try:
        from cua.detection.visual_detector import VisualDetector
        
        # Initialize detector
        print("Initializing visual detector...")
        detector = VisualDetector()
        
        # Test screenshot capture
        print("Capturing and processing screenshot...")
        screenshot = detector.capture_screenshot()
        
        # Test OWLv2 processing with the fixed image format
        print("Testing OWLv2 detection with format fix...")
        labels = ["chat input box", "text input"]
        result = detector.detect_with_owlv2(screenshot, labels)
        
        if result:
            x, y, width, height = result
            print(f"SUCCESS! Detection worked: ({x}, {y}, {width}, {height})")
        else:
            print("No detection found, but processing completed without errors")
            print("This might be normal if no chat input box is visible")
        
        print("Image format fix successful!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_image_processing()
    
    if success:
        print("\nImage format fix working!")
        print("Now try the cursor detection test again:")
        print("python test_cursor_detection.py")
    else:
        print("\nStill having issues. Let's debug further.")