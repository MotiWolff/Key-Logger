from abc import ABC, abstractmethod
from typing import List

class IWriter(ABC):
    @abstractmethod
    def write(self, data: List[str]) -> bool:
        """Write data to the destination"""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Ensure all data is written"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close any open resources"""
        pass 