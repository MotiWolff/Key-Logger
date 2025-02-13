class Encryptor:
    def __init__(self, key: str = "default_key"):
        """Initialize encryptor with a key"""
        self.key = key.encode()
        self.key_length = len(self.key)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt data using XOR encryption"""
        data_bytes = data.encode()
        encrypted = bytearray()
        
        for i in range(len(data_bytes)):
            encrypted.append(data_bytes[i] ^ self.key[i % self.key_length])
            
        return bytes(encrypted)
    
    def decrypt(self, data: bytes) -> str:
        """Decrypt data using XOR encryption"""
        decrypted = bytearray()
        
        for i in range(len(data)):
            decrypted.append(data[i] ^ self.key[i % self.key_length])
            
        return decrypted.decode()
