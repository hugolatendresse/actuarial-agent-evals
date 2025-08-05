# Cursor UI Agent (CUA) Integration

Automated visual interaction with Cursor for actuarial AI testing.

## Structure

- `detection/` - Computer vision modules for UI element detection
- `actions/` - Mouse/keyboard automation modules  
- `config/` - Configuration and API key management
- `tests/` - CUA-specific testing modules
- `integration/` - Integration with main harness system

## Usage

The CUA automatically handles the manual steps currently done in harness.py:
1. Opens new Cursor chat (Ctrl+N)
2. Pastes prompts (Ctrl+V) 
3. Submits prompts (Enter)
4. Monitors responses

## Dependencies

- OWLv2 (Hugging Face) for object detection
- Qwen-VL (DeepInfra) for fallback detection
- pyautogui for mouse/keyboard control
- PIL for screenshot capture