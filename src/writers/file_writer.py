import os
from datetime import datetime
from typing import List
import logging
from .interfaces import IWriter
from ..encryption.encryptor import Encryptor
import time

class FileWriter(IWriter):
    def __init__(self, encryption_key: str = "default_key", base_path: str = None, device_id=None):
        # Set base_path to backend/data if not specified
        self.base_path = base_path or os.path.join('backend', 'data')
        self.device_id = device_id
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
        if not data or not self.device_id:
            self.logger.warning("No data or device ID provided")
            return False
            
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
        
    def _rotate_logs(self) -> None:
        """Rotate logs if they exceed size limit"""
        try:
            max_size = 10 * 1024 * 1024  # 10MB
            if self.current_file and os.path.exists(self.current_file.name):
                if os.path.getsize(self.current_file.name) > max_size:
                    self.close()
                    self._archive_old_log()
                    self._open_file()
        except Exception as e:
            self.logger.error(f"Error rotating logs: {e}")
            raise

    def _archive_old_log(self) -> None:
        """Archive old logs and clean up if needed"""
        try:
            archive_dir = os.path.join(self.base_path, 'archive')
            os.makedirs(archive_dir, exist_ok=True)
            
            # Move file to archive
            old_path = self.current_file.name
            new_path = os.path.join(archive_dir, 
                                  f"keylog_{time.strftime('%Y%m%d_%H%M%S')}.txt")
            os.rename(old_path, new_path)
            
            # Clean up old archives (keep last 10)
            self._cleanup_old_archives(archive_dir)
        except Exception as e:
            self.logger.error(f"Error archiving log: {e}")
            raise

    def _cleanup_old_archives(self, archive_dir: str, keep_last: int = 10) -> None:
        """Clean up old archive files, keeping only the specified number of most recent files"""
        try:
            files = sorted([os.path.join(archive_dir, f) for f in os.listdir(archive_dir)
                          if f.startswith('keylog_')])
            for old_file in files[:-keep_last]:
                os.remove(old_file)
        except Exception as e:
            self.logger.error(f"Error cleaning up archives: {e}")

class LogWriter:
    def __init__(self, base_path='backend/data', device_id=None):
        self.device_id = device_id
        self.encryptor = Encryptor()
        print(f"LogWriter initialized with device_id: {device_id}")

    def write(self, content: str):
        try:
            if not content or not self.device_id:
                return
                
            # Encrypt the content
            encrypted_content = self.encryptor.encrypt(content)
            
            # Store in MongoDB
            # db.logs.insert_one({
            #     "device_id": self.device_id,
            #     "content": encrypted_content,
            #     "timestamp": datetime.now()
            # })
                
        except Exception as e:
            print(f"Error writing log: {e}")

    def read(self, filename: str) -> str:
        try:
            filepath = os.path.join(self.base_path, filename)
            if not os.path.exists(filepath):
                return ""
                
            with open(filepath, 'r') as f:
                return f.read().strip()
                
        except Exception as e:
            print(f"Error reading log: {e}")
            return "" 