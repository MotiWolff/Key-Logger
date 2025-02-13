from src.keylogger.mac_keylogger import MacKeyLogger
from src.writers.file_writer import FileWriter
import time

def test_keylogger():
    print("Starting MacKeyLogger test...")
    print("Press some keys. Press Ctrl+C to stop.")
    
    try:
        # Initialize the writer and keylogger
        writer = FileWriter()
        keylogger = MacKeyLogger()
        
        # Start logging
        keylogger.start_logging()
        print("Keylogger started successfully!")
        
        # Keep running and write captured keys every 5 seconds
        while True:
            time.sleep(5)
            keys = keylogger.get_logged_keys()
            if keys:
                print("Captured keys:", ''.join(keys))
                writer.write(keys)
                
    except KeyboardInterrupt:
        print("\nStopping keylogger...")
        keylogger.stop_logging()
        writer.close()
        print("Keylogger stopped.")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    test_keylogger() 