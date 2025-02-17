from cryptography.fernet import Fernet
import base64
import os

class Encryptor:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        elif isinstance(key, str):
            # If key is a string, derive a proper Fernet key
            key = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
        self.fernet = Fernet(key)

    def encrypt(self, text: str) -> str:
        if not text:
            return ""
        try:
            text_bytes = text.encode('utf-8')
            encrypted_bytes = self.fernet.encrypt(text_bytes)
            return f"ENC:{base64.b64encode(encrypted_bytes).decode('utf-8')}"
        except Exception as e:
            print(f"Encryption error: {e}")
            return text

    def decrypt(self, encrypted_text: str) -> str:
        if not encrypted_text or not isinstance(encrypted_text, str):
            return str(encrypted_text)
            
        if not encrypted_text.startswith("ENC:"):
            return encrypted_text
        
        try:
            base64_text = encrypted_text[4:]
            encrypted_bytes = base64.b64decode(base64_text)
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_text