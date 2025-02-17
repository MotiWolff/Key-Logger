import subprocess
import platform
from typing import Tuple
import os

class MacPermissionError(Exception):
    """Custom exception for MacOS permission issues"""
    pass

class PermissionChecker:
    @staticmethod
    def check_macos_permissions() -> Tuple[bool, str]:
        """
        Check MacOS accessibility and input monitoring permissions
        Returns: (has_permission: bool, message: str)
        """
        if platform.system() != 'Darwin':
            return True, "Not MacOS"

        try:
            # Check Accessibility permissions
            acc_cmd = 'tccutil status Accessibility com.apple.Terminal'
            acc_result = subprocess.run(acc_cmd.split(), capture_output=True, text=True)
            
            # Check Input Monitoring permissions
            input_cmd = 'tccutil status InputMonitoring com.apple.Terminal'
            input_result = subprocess.run(input_cmd.split(), capture_output=True, text=True)
            
            if "DENIED" in acc_result.stdout or "DENIED" in input_result.stdout:
                return False, "Missing required permissions"
                
            return True, "All permissions granted"

        except subprocess.SubprocessError as e:
            raise MacPermissionError(f"Error checking permissions: {str(e)}")
        
    @staticmethod
    def request_macos_permissions() -> None:
        """Request necessary MacOS permissions"""
        try:
            # Open Security & Privacy preferences
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.preference.security'
            ])
            
            print("\nPlease enable the following permissions:")
            print("1. System Settings -> Privacy & Security -> Accessibility")
            print("2. System Settings -> Privacy & Security -> Input Monitoring")
            print("\nAfter enabling permissions, restart the application.")
            
        except subprocess.SubprocessError as e:
            raise MacPermissionError(f"Error requesting permissions: {str(e)}")

    @staticmethod
    def check_file_permissions(path: str) -> bool:
        """Check if we have write permissions to the log file location"""
        try:
            # Check if directory exists and is writable
            dir_path = os.path.dirname(os.path.abspath(path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # Test file writing
            test_file = os.path.join(dir_path, '.permission_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return True
        except (OSError, IOError):
            return False