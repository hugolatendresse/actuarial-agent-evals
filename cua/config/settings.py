"""
Configuration settings for Cursor UI Agent (CUA)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CUAConfig:
    """Configuration class for CUA settings"""
    
    # API Keys
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
    DEEPINFRA_API_KEY = os.getenv('DEEPINFRA_TOKEN')  # Use DEEPINFRA_TOKEN from .env
    
    # Model endpoints
    OWLV2_MODEL = "google/owlv2-base-patch16-ensemble"
    QWEN_VL_MODEL = "Qwen/Qwen2.5-VL-32B-Instruct"
    QWEN_VL_ENDPOINT = "https://api.deepinfra.com/v1/openai/chat/completions"  # Legacy API endpoint
    
    # Detection settings
    MIN_BOX_WIDTH = 100
    MIN_BOX_HEIGHT = 30
    CONFIDENCE_THRESHOLD = 0.3
    
    # Timing settings (in seconds)
    SCREENSHOT_DELAY = 0.5
    CLICK_DELAY = 0.3
    TYPE_DELAY = 0.1
    PHASE_WAIT_TIME = 3.0
    
    # UI element labels for detection
    CHAT_INPUT_LABELS = [
        "chat input box",
        "text input",
        "message input",
        "chat textbox",
        "cursor chat input field",
        "AI chat input box",
        "code editor chat input",
        "composer input field",
        "Plan, search, build anything",
        "Active Tab"
    ]
    
    # Test prompts
    PHASE1_PROMPT = "Create an HTML page that says 'Hello World'"
    PHASE2_PROMPT = """Generate a high-level list of pages/screens for a typical web application. 
Provide the output in Markdown format using headings and bullet points."""
    
    # Screen resolution settings
    SCREENSHOT_REGION = None  # None for full screen, or (x, y, width, height)
    
    @classmethod
    def validate(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not cls.HUGGINGFACE_TOKEN:
            missing_keys.append("HUGGINGFACE_TOKEN")
        if not cls.DEEPINFRA_API_KEY:
            missing_keys.append("DEEPINFRA_TOKEN")
            
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True