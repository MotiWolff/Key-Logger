import os
from datetime import datetime
from typing import List
import logging
from .interfaces import IWriter
from ..encryption.encryptor import Encryptor

class FileWriter(IWriter):
    def __init__(self, encryption_key: str = "default_key", base_path: str = None):
        # Set base_path to backend/data if not specified
        self.base_path = base_path or os.path.join('backend', 'data')
        self.current_file = None
        self.current_date = None
        self.encryptor = Encryptor(encryption_key)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Ensure data directory exists
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist"""
        try:
            os.makedirs(self.base_path, exist_ok=True)
            self.logger.info(f"Log directory ensured: {self.base_path}")
        except Exception as e:
            self.logger.error(f"Failed to create log directory: {e}")
            raise
    
    def _get_log_file_path(self) -> str:
        """Generate log file path for current date"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.base_path, f"keylog_{current_date}.txt")
    
    def _open_file(self) -> None:
        """Open or rotate log file if needed"""
        try:
            new_date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if we need to rotate to a new file
            if self.current_date != new_date:
                self.close()  # Close current file if open
                
                file_path = self._get_log_file_path()
                self.current_file = open(file_path, 'a', encoding='utf-8')
                self.current_date = new_date
                
                self.logger.info(f"Opened new log file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to open log file: {e}")
            raise

    def write(self, data: List[str]) -> bool:
        """Write encrypted data to the log file"""
        if not data:
            return True
            
        try:
            self._open_file()
            
            # Join and encrypt the data
            content = ''.join(data)
            if not content.endswith('\n'):
                content += '\n'
            
            # Encrypt and format as hex
            encrypted_data = self.encryptor.encrypt(content)
            hex_data = encrypted_data.hex()
            
            # Write with clear separation
            self.current_file.write(f"ENC:{hex_data}\n")
            self.current_file.flush()
            
            self.logger.debug(f"Written encrypted data to log file")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write to log file: {e}")
            return False
    
    def flush(self) -> None:
        """Flush any buffered data"""
        try:
            if self.current_file:
                self.current_file.flush()
                self.logger.debug("File buffer flushed")
        except Exception as e:
            self.logger.error(f"Failed to flush file buffer: {e}")
            raise
    
    def close(self) -> None:
        """Close the current log file"""
        try:
            if self.current_file:
                self.current_file.close()
                self.current_file = None
                self.current_date = None
                self.logger.info("Log file closed")
        except Exception as e:
            self.logger.error(f"Failed to close log file: {e}")
            raise
    
    def __del__(self):
        """Ensure file is closed on object destruction"""
        self.close() 