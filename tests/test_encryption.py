import unittest
from src.encryption.encryptor import Encryptor

class TestEncryptor(unittest.TestCase):
    def setUp(self):
        self.encryptor = Encryptor("test_key")
        self.test_data = "Hello, World!"

    def test_encryption_decryption(self):
        # Test that encryption followed by decryption returns original data
        encrypted = self.encryptor.encrypt(self.test_data)
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(self.test_data, decrypted)

    def test_different_keys(self):
        # Test that different keys produce different results
        encryptor1 = Encryptor("key1")
        encryptor2 = Encryptor("key2")
        
        encrypted1 = encryptor1.encrypt(self.test_data)
        encrypted2 = encryptor2.encrypt(self.test_data)
        
        self.assertNotEqual(encrypted1, encrypted2)

    def test_empty_string(self):
        # Test handling of empty string
        empty = ""
        encrypted = self.encryptor.encrypt(empty)
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(empty, decrypted)

if __name__ == '__main__':
    unittest.main()
