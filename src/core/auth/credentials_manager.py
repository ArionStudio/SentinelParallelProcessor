import os
from typing import Optional
from dataclasses import dataclass
from .secure_storage import SecureStorage

@dataclass
class Credentials:
    client_id: str
    client_secret: str

class CredentialsManager:
    def __init__(self, storage_file: str = "sentinel_config.enc"):
        self.storage = SecureStorage(storage_file)

    def save_credentials(self, credentials: Credentials, password: str) -> bool:
        """Save credentials to encrypted storage (password is only for encryption)"""
        try:
            config = {
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret
            }
            # Initialize encryption with the user's password
            self.storage.initialize_encryption(password)
            return self.storage.save_data(config)
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False

    def load_credentials(self, password: str) -> Optional[Credentials]:
        """Load credentials from encrypted storage (password is only for decryption)"""
        try:
            config = self.storage.load_data(password)
            if config:
                return Credentials(
                    client_id=config.get("client_id", ""),
                    client_secret=config.get("client_secret", "")
                )
            return None
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

    def validate_credentials(self, credentials: Credentials) -> bool:
        """Validate that all required fields are present"""
        return all([
            credentials.client_id.strip(),
            credentials.client_secret.strip()
        ])

    def clear_credentials(self) -> bool:
        """Clear stored credentials"""
        return self.storage.clear_data() 