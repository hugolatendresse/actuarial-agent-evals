import os
import time
import shutil
import platform
import subprocess
import pyperclip
import pyautogui
from pathlib import Path
from typing import Optional, Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def get_platform_keys(ide_name: Optional[str] = None) -> Dict[str, Optional[List[str]]]:
    """Get the correct key combinations for the current platform and IDE."""
    system = platform.system().lower()
    
    if system == 'darwin':
        base_keys = {
            'chat_activate': ['command', 'l'],
            'new_chat': ['command', 'n'],
            'paste': ['command', 'v']
        }
    else:
        base_keys = {
            'chat_activate': ['ctrl', "'"],
            'new_chat': ['ctrl', 'alt', 'n'],
            'paste': ['ctrl', 'v'],
        }
    
    if ide_name and ide_name.lower() == 'continue':
        base_keys['new_chat'] = None
    elif ide_name and ide_name.lower() == 'cline':
        if system == 'darwin':
            base_keys['chat_activate'] = ['command', '\'']
        else:
            base_keys['chat_activate'] = ['ctrl', '\'']
    
    return base_keys


@staticmethod
def enter_keybinding(paste_keys: list[str], delay_between: float = 1.0):
    for key in paste_keys:
        pyautogui.keyDown(key)
        time.sleep(0.1)

    for key in paste_keys[::-1]:
        pyautogui.keyUp(key)
        time.sleep(0.1)

    time.sleep(delay_between)


class FileWatcher:
    """Watches for solution files to be created and marked complete."""
    
    def __init__(self, filename_to_watch: str, workspace_dir: Path, completion_marker: str):
        self.filename_to_watch = filename_to_watch
        self.workspace_dir = workspace_dir
        self.completion_marker = completion_marker
        self.file_path = None
        self.file_ready = False
        self.observer = None
    
    def _has_completion_marker(self, file_path: Path) -> bool:
        """Check if the solution has the completion marker."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.completion_marker in content
        except (IOError, UnicodeDecodeError):
            return False
    
    def on_created(self, event):
        """Called when a file is created."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"\nDetected '{self.filename_to_watch}' created.")
            self.file_path = event.src_path
            
            if self._has_completion_marker(event.src_path):
                print(f"'{self.completion_marker}' marker found. File is ready.")
                self.file_ready = True
            else:
                print(f"Waiting for '{self.completion_marker}' marker...")
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename_to_watch:
            print(f"Detected '{self.filename_to_watch}' has been saved.")
            self.file_path = event.src_path
            
            if self._has_completion_marker(event.src_path):
                print(f"'{self.completion_marker}' marker found. File is ready.")
                self.file_ready = True
            else:
                print(f"Waiting for '{self.completion_marker}' marker...")
    
    def wait_for_completion(self) -> Path:
        """Wait for the file to be created and marked complete."""
        # Check if file already exists with completion marker
        existing_file = self.workspace_dir / self.filename_to_watch
        if existing_file.exists() and self._has_completion_marker(existing_file):
            print(f"'{self.filename_to_watch}' already exists with completion marker.")
            self.file_path = str(existing_file)
            self.file_ready = True
            return existing_file
        
        handler = FileSystemEventHandler()
        handler.on_created = self.on_created
        handler.on_modified = self.on_modified
        
        self.observer = Observer()
        self.observer.schedule(handler, str(self.workspace_dir), recursive=False)
        self.observer.start()
        
        try:
            while not self.file_ready:
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()
        
        return Path(self.file_path)


class IDEAutomation:
    """Handles IDE-specific automation for prompt delivery."""
    
    SUPPORTED_IDES = ['cursor', 'continue', 'cline']
    
    @staticmethod
    def is_supported(ide_name: str) -> bool:
        """Check if auto mode is supported for the given IDE."""
        return ide_name.lower() in IDEAutomation.SUPPORTED_IDES
    
    @staticmethod
    def automate_input(
        prompt_text: str,
        ide_name: str,
        is_first_question: bool = True,
        delay_before: float = 2.0,
        delay_between: float = 1.0,
    ) -> bool:
        """Automate the process of pasting prompt into the specified IDE."""
        keys = get_platform_keys(ide_name)
        
        print(f"Automating {ide_name} input...")
        
        for i in range(int(delay_before), 0, -1):
            print(f"   Starting in {i}...")
            time.sleep(1.0)
        
        try:
            system = platform.system().lower()
            if system == 'darwin':
                ide_app_name = "Cursor" if ide_name.lower() == "cursor" else ide_name.title()
                print(f"Attempting to activate {ide_app_name} application...")
                try:
                    subprocess.run(
                        ['osascript', '-e', f'tell application "{ide_app_name}" to activate'],
                        check=False,
                        capture_output=True
                    )
                    time.sleep(1.0)
                except Exception as e:
                    print(f"Could not activate {ide_app_name} app: {e}")
                    print(f"Please make sure {ide_app_name} is manually focused.")
            
            should_activate_chat = is_first_question or (ide_name and ide_name.lower() == 'continue')
            if should_activate_chat:
                print("   → Activating chat...")
                chat_keys = keys['chat_activate']
                
                enter_keybinding(chat_keys, delay_between=delay_between)
            
            if keys['new_chat'] is not None:
                print("   → Creating new chat...")
                new_chat_keys = keys['new_chat']
                enter_keybinding(new_chat_keys, delay_between=delay_between)
                print("   → Confirming new chat...")
                pyautogui.press('enter')
                time.sleep(delay_between)
            else:
                print("   → Skipping new chat creation (not supported by this IDE)")
                time.sleep(delay_between)
            
            print("   → Pasting prompt...")
            paste_keys = keys['paste']


            enter_keybinding(paste_keys, delay_between=delay_between)
            
            print("   → Submitting prompt...")
            pyautogui.press('enter')
            
            print("Automation completed successfully!")
            return True
            
        except Exception as e:
            print(f"Automation failed: {e}")
            print("Please manually paste the prompt from clipboard.")
            return False


class WorkspaceManager:
    """Manages test workspace directories."""
    
    @staticmethod
    def create_workspace(workspace_dir: Path, clean: bool = True) -> Path:
        """Create or clean a workspace directory."""
        if clean and workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir
    
    @staticmethod
    def write_file(file_path: Path, content: str) -> None:
        """Write content to a file."""
        with open(file_path, 'w') as f:
            f.write(content)


class PromptHandler:
    """Handles prompt generation and clipboard operations."""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Copy text to clipboard."""
        try:
            pyperclip.copy(text)
            print("Prompt copied to clipboard.")
            return True
        except Exception as e:
            print(f"Could not copy to clipboard: {e}")
            print("--- PROMPT ---")
            print(text)
            print("--------------")
            return False
    
    @staticmethod
    def display_instructions(
        workspace_dir: Path,
        filename: str,
        ide_name: str,
        mode: str,
        is_first_question: bool = True
    ) -> None:
        """Display instructions for user action."""
        print("\n" + "=" * 80)
        print("ACTION REQUIRED - OPEN WORKSPACE IN IDE")
        print("=" * 80)
        print(f"Workspace directory: {workspace_dir.absolute()}")
        print(f"File to edit:        {filename}")
        print("")
        print(f"IMPORTANT: Open this EXACT folder in {ide_name}:")
        print(f"  {workspace_dir.absolute()}")
        print("")
        print(f"The AI will work in this isolated workspace.")
        print("")
        
        if mode == 'auto':
            print("The system will automatically:")
            if ide_name.lower() == 'continue':
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            elif ide_name.lower() == 'cline':
                print("   - Activate chat (Cmd+' or Ctrl+')")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
            else:
                print("   - Activate chat (Cmd+L or Ctrl+L)")
                print("   - Create a new chat (Cmd+N or Ctrl+N)")
                print("   - Paste the prompt (Cmd+V or Ctrl+V)")
                print("   - Submit the prompt (Enter)")
        else:
            print("Generate the solution using the prompt from your clipboard:")
            if ide_name.lower() == 'continue':
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
            elif ide_name.lower() == 'cline':
                print(f"   - Press Cmd+' (Mac) or Ctrl+' (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            else:
                print(f"   - Press Cmd+L (Mac) or Ctrl+L (Windows/Linux) to activate {ide_name} chat")
                print("   - Press Cmd+N (Mac) or Ctrl+N (Windows/Linux) to create a new chat")
            print("   - Press Cmd+V (Mac) or Ctrl+V (Windows/Linux) to paste the prompt")
            print("   - Press Enter to submit")

