#!/usr/bin/env python3
"""
Setup script for Cursor UI Agent (CUA)
Run this to set up CUA in actuarial AI project
"""
import os
import sys
import subprocess


def check_python_version():
    """Check Python version is compatible"""
    if sys.version_info < (3, 9):
        print("Python 3.9+ required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling CUA dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template"""
    env_path = ".env"
    template_path = ".env.template"
    
    if os.path.exists(env_path):
        print(f"⚠️  .env file already exists")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            return True
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(template_content)
        
        print(f"Created {env_path} from template")
        print("Please edit .env and add your API keys:")
        print("   - HUGGINGFACE_TOKEN (from https://huggingface.co/settings/tokens)")
        print("   - DEEPINFRA_API_KEY (from https://deepinfra.com/)")
        return True
    else:
        print(f"Template file {template_path} not found")
        # Create a basic .env file
        with open(env_path, "w") as f:
            f.write("""# CUA Configuration
# Get Hugging Face token from: https://huggingface.co/settings/tokens
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Get DeepInfra API key from: https://deepinfra.com/
DEEPINFRA_API_KEY=your_deepinfra_api_key_here
""")
        print(f"Created basic {env_path} file")
        print("Please edit .env and add your API keys")
        return True


def test_imports():
    """Test that CUA can be imported"""
    print("\nTesting CUA imports...")
    
    try:
        from cua import CursorUIAgent, create_harness_integrator
        print("CUA imports successful")
        return True
    except ImportError as e:
        print(f"CUA import failed: {e}")
        return False


def check_cursor_status():
    """Check if Cursor is available for testing"""
    print("\nChecking Cursor availability...")
    
    try:
        # Try to take a screenshot to see if we can detect anything
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        print(f"Screenshot capture working (resolution: {screenshot.size})")
        
        print("\nChecklist:")
        print("   □ Cursor application is installed")
        print("   □ Cursor is currently open")
        print("   □ A chat interface is visible") 
        print("   □ Screen is not locked or covered")
        
        ready = input("\nIs Cursor ready for testing? (y/n): ").strip().lower()
        return ready == 'y'
        
    except Exception as e:
        print(f"Screenshot test failed: {e}")
        return False


def run_basic_test():
    """Run a basic CUA functionality test"""
    print("\nRunning basic CUA test...")
    
    try:
        from cua import create_harness_integrator
        
        # Create integrator in test mode
        integrator = create_harness_integrator(enable_automation=True)
        
        # Print status
        integrator.print_status()
        
        # Try validation if user wants
        test_validation = input("\nRun Cursor responsiveness test? (y/n): ").strip().lower()
        if test_validation == 'y':
            success = integrator.validate_cursor_responsiveness()
            if success:
                print("✅ Cursor responsiveness test passed!")
            else:
                print("⚠️  Cursor responsiveness test failed")
                print("   This might be okay - you can still use manual fallback mode")
        
        return True
        
    except Exception as e:
        print(f"CUA test failed: {e}")
        return False


def show_next_steps():
    """Show what to do next"""
    print("\nNext Steps:")
    print("1. Edit .env file with your API keys")
    print("2. Test CUA: python test_cua.py")
    print("3. Integrate with harness: see harness_cua_integration_example.py")
    print("4. Run automated tests: python harness.py")
    
    print("\nDocumentation:")
    print("- CUA structure: cua/README.md")
    print("- Integration guide: harness_cua_integration_example.py")
    print("- Test script: test_cua.py")
    
    print("\nTroubleshooting:")
    print("- If automation fails, CUA falls back to manual mode")
    print("- Make sure Cursor is open and visible")
    print("- Check API keys in .env file")
    print("- Run test_cua.py to validate setup")


def main():
    """Main setup function"""
    print("Cursor UI Agent (CUA) Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create environment file
    if not create_env_file():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Check Cursor status
    cursor_ready = check_cursor_status()
    
    # Run basic test if Cursor is ready
    if cursor_ready:
        run_basic_test()
    else:
        print("Skipping Cursor test - set up API keys and try test_cua.py later")
    
    # Show next steps
    show_next_steps()
    
    print("\nCUA setup complete!")
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)