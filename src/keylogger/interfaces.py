from abc import ABC, abstractmethod
from typing import List

class IKeyLogger(ABC):
    @abstractmethod
    def start_logging(self) -> None:
        """Start the keyboard listener"""
        pass
    
    @abstractmethod
    def stop_logging(self) -> None:
        """Stop the keyboard listener"""
        pass
    
    @abstractmethod
    def get_logged_keys(self) -> List[str]:
        """Return all captured keystrokes"""
        pass 