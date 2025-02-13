from src.encryption.encryptor import Encryptor
import sys

def read_encrypted_log(file_path: str, key: str = "your_secret_key"):
    encryptor = Encryptor(key)
    
    print(f"Reading log file: {file_path}")
    print("Decrypted content:")
    print("-" * 50)
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    # Skip empty lines
                    if not line.strip():
                        continue
                        
                    # Check for encryption marker
                    if line.startswith("ENC:"):
                        # Get the hex data after the marker
                        hex_data = line[4:].strip()
                        # Convert hex to bytes and decrypt
                        encrypted_data = bytes.fromhex(hex_data)
                        decrypted = encryptor.decrypt(encrypted_data)
                        print(decrypted, end='')
                    else:
                        print(f"Skipping invalid line: {line.strip()}")
                except ValueError as e:
                    print(f"Error processing line: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    print("\n" + "-" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_logs.py <log_file_path>")
        sys.exit(1)
        
    read_encrypted_log(sys.argv[1]) 