import os
import json
from base64 import b64encode, b64decode
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

class SecureStorage:
    def __init__(self, storage_file: str = "sentinel_config.enc"):
        self.storage_file = storage_file
        self._key = None
        self._fernet = None
        # Load .env file
        load_dotenv()
        # Get salt from .env file
        self._salt = os.getenv('SENTINEL_SALT', 'default_salt_for_development').encode()

    def initialize_encryption(self, password: str):
        """Initialize encryption with user password"""
        # Generate a key using PBKDF2 with salt from .env
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        
        # Use the user's password for key derivation
        key = kdf.derive(password.encode())
        self._key = b64encode(key)
        self._fernet = Fernet(self._key)

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save encrypted data to file"""
        if not self._fernet:
            raise ValueError("Encryption not initialized. Call initialize_encryption first.")

        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            
            # Encrypt the data
            encrypted_data = self._fernet.encrypt(json_data.encode())
            
            # Save to file
            with open(self.storage_file, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Error saving encrypted data: {e}")
            return False

    def load_data(self, password: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt data from file"""
        if not os.path.exists(self.storage_file):
            return None

        try:
            # Initialize encryption with the provided password
            self.initialize_encryption(password)
            
            # Read encrypted data
            with open(self.storage_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            # Parse JSON
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error loading encrypted data: {e}")
            return None

    def clear_data(self) -> bool:
        """Clear stored data"""
        try:
            if os.path.exists(self.storage_file):
                os.remove(self.storage_file)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False 