"""
Visual detection module for CUA using OWLv2 and Qwen-VL
"""
import io
import base64
import requests
from PIL import Image, ImageGrab, ImageDraw
from transformers import Owlv2Processor, Owlv2ForObjectDetection
import torch
from typing import Tuple, Optional, List

from ..config.settings import CUAConfig


class VisualDetector:
    """Main class for detecting UI elements using computer vision"""
    
    def __init__(self):
        self.config = CUAConfig()
        # OWLv2 components
        self.processor = None
        self.model = None
        
        self._load_owlv2_model()
    
    def _load_owlv2_model(self):
        """Load OWLv2 model and processor"""
        try:
            self.processor = Owlv2Processor.from_pretrained(
                self.config.OWLV2_MODEL,
                token=self.config.HUGGINGFACE_TOKEN
            )
            self.model = Owlv2ForObjectDetection.from_pretrained(
                self.config.OWLV2_MODEL,
                token=self.config.HUGGINGFACE_TOKEN
            )
            print("✓ OWLv2 model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load OWLv2 model: {e}")
            self.processor = None
            self.model = None
    

    
    def capture_screenshot(self, save_debug=True) -> Image.Image:
        """Capture screenshot of the current screen"""
        if self.config.SCREENSHOT_REGION:
            screenshot = ImageGrab.grab(bbox=self.config.SCREENSHOT_REGION)
        else:
            screenshot = ImageGrab.grab()
        
        # Ensure screenshot is in RGB format
        if screenshot.mode != 'RGB':
            screenshot = screenshot.convert('RGB')
            
        print(f"Screenshot captured: {screenshot.size} pixels, mode: {screenshot.mode}")
        
        # Save debug screenshot
        if save_debug:
            import os
            debug_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_screenshot.png")
            screenshot.save(debug_path)
            print(f"Debug screenshot saved to: {debug_path}")
        
        return screenshot
    
    def detect_with_owlv2(self, image: Image.Image, target_labels: List[str]) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect target UI element using OWLv2
        Returns: (x, y, width, height) of detected box or None
        """
        if not self.processor or not self.model:
            return None
        
        try:
            # Ensure image is in RGB format for OWLv2
            if image.mode != 'RGB':
                print(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            print(f"Processing image: {image.size} pixels, mode: {image.mode}")
            print(f"Looking for labels: {target_labels}")
            
            # Prepare inputs
            inputs = self.processor(text=target_labels, images=image, return_tensors="pt")
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process results
            target_sizes = torch.Tensor([image.size[::-1]])
            results = self.processor.post_process_object_detection(
                outputs=outputs, 
                target_sizes=target_sizes, 
                threshold=self.config.CONFIDENCE_THRESHOLD
            )[0]
            
            print(f"OWLv2 found {len(results['boxes'])} potential matches")
            
            # Save visualization of all detections
            self._visualize_detections(image, results, "owlv2_detections.png")
            
            # Find best detection
            if len(results["boxes"]) > 0:
                # Get the box with highest score
                best_idx = torch.argmax(results["scores"])
                box = results["boxes"][best_idx].cpu().numpy()
                score = results["scores"][best_idx].item()
                
                x, y, x2, y2 = map(int, box)
                width, height = x2 - x, y2 - y
                
                print(f"Best detection: box=({x}, {y}, {width}, {height}), confidence={score:.3f}")
                
                # Validate box dimensions
                if self._validate_detection(x, y, width, height, image.size):
                    return (x, y, width, height)
                else:
                    print("Detection failed validation (too small or out of bounds)")
            
            return None
            
        except Exception as e:
            print(f"OWLv2 detection failed: {e}")
            import traceback
            print(f"Full error details: {traceback.format_exc()}")
            return None
    
    def detect_with_qwen_vl(self, image: Image.Image, reference_image_path: str = None) -> Optional[Tuple[int, int, int, int]]:
        """
        Fallback detection using Qwen-VL API with reference image comparison
        Returns: (x, y, width, height) of detected box or None
        """
        try:
            import os
            
            # Use provided reference image or default cursor input reference
            if reference_image_path is None:
                reference_image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "cursor_input_reference.png"
                )
            
            # Load and convert reference image to base64
            reference_image = Image.open(reference_image_path)
            ref_buffer = io.BytesIO()
            reference_image.save(ref_buffer, format='PNG')
            ref_image_b64 = base64.b64encode(ref_buffer.getvalue()).decode()
            
            # Convert screenshot to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.config.DEEPINFRA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Two-image comparison prompt as described in original article
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "I will show you two images. The first is a reference example of a chat input box. The second is a screenshot where I need to find a similar chat input box. Please compare the visual similarities and find the chat input box in the screenshot that looks most like the reference. Return only the bounding box coordinates as 'x,y,width,height' format."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{ref_image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": "Reference chat input box above. Now find a similar one in this screenshot:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            }]
            
            payload = {
                "model": self.config.QWEN_VL_MODEL,
                "messages": messages,
                "max_tokens": 150
            }
            
            response = requests.post(self.config.QWEN_VL_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"Qwen-VL response: {content}")
                
                # Parse coordinates from response
                coords = self._parse_coordinates(content)
                if coords and self._validate_detection(*coords, image.size):
                    return coords
            else:
                print(f"Qwen-VL API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            print(f"Qwen-VL detection failed: {e}")
            import traceback
            print(f"Full error details: {traceback.format_exc()}")
            return None
    
    def _parse_coordinates(self, text: str) -> Optional[Tuple[int, int, int, int]]:
        """Parse coordinates from Qwen-VL response text"""
        try:
            # Look for comma-separated numbers
            import re
            pattern = r'(\d+),(\d+),(\d+),(\d+)'
            match = re.search(pattern, text)
            
            if match:
                # Qwen-VL returns (x1, y1, x2, y2) format, convert to (x, y, width, height)
                x1, y1, x2, y2 = map(int, match.groups())
                x, y = x1, y1
                width = x2 - x1
                height = y2 - y1
                print(f"Parsed coordinates: ({x}, {y}, {width}, {height})")
                return (x, y, width, height)
            return None
        except Exception as e:
            print(f"Coordinate parsing error: {e}")
            return None
    
    def _visualize_detections(self, image: Image.Image, results: dict, filename: str):
        """Save an image with bounding boxes drawn on it for debugging"""
        try:
            import os
            
            # Create a copy to draw on
            debug_image = image.copy()
            draw = ImageDraw.Draw(debug_image)
            
            # Draw all detected boxes
            boxes = results.get("boxes", [])
            scores = results.get("scores", [])
            
            for i, (box, score) in enumerate(zip(boxes, scores)):
                x, y, x2, y2 = map(int, box.cpu().numpy())
                
                # Choose color based on score
                if score > 0.5:
                    color = "green"
                elif score > 0.3:
                    color = "orange"
                else:
                    color = "red"
                
                # Draw bounding box
                draw.rectangle([x, y, x2, y2], outline=color, width=3)
                
                # Draw score label
                label = f"{score:.3f}"
                draw.text((x, y-20), label, fill=color)
            
            # Save the debug image
            debug_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), filename)
            debug_image.save(debug_path)
            print(f"Detection visualization saved to: {debug_path}")
            
        except Exception as e:
            print(f"Could not save detection visualization: {e}")
    
    def _validate_detection(self, x: int, y: int, width: int, height: int, image_size: Tuple[int, int]) -> bool:
        """Validate that detected box meets minimum requirements"""
        img_width, img_height = image_size
        
        # Check minimum dimensions
        if width < self.config.MIN_BOX_WIDTH or height < self.config.MIN_BOX_HEIGHT:
            return False
        
        # Check if box is within image bounds
        if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
            return False
        
        # Check if box is not in top-left corner (common false positive)
        if x < 50 and y < 50:
            return False
        
        return True
    
    def detect_chat_input(self) -> Optional[Tuple[int, int]]:
        """
        Main detection method that tries OWLv2 first, then Qwen-VL
        Returns: (center_x, center_y) of detected input box or None
        """
        print("📸 Capturing screenshot...")
        image = self.capture_screenshot(save_debug=True)
        
        # Try OWLv2 first
        print("🔍 Attempting OWLv2 detection...")
        detection = self.detect_with_owlv2(image, self.config.CHAT_INPUT_LABELS)
        
        if detection:
            print("✓ OWLv2 detection successful")
        else:
            print("⚠ OWLv2 failed, trying Qwen-VL fallback...")
            detection = self.detect_with_qwen_vl(image)
            
            if detection:
                print("✓ Qwen-VL fallback successful")
            else:
                print("✗ Both detection methods failed")
                return None
        
        # Calculate center point
        x, y, width, height = detection
        center_x = x + width // 2
        center_y = y + height // 2
        
        print(f"Input box detected at center: ({center_x}, {center_y})")
        return (center_x, center_y)