from typing import Optional

# The only imports needed from sentinelhub-py are for configuration and testing.
from sentinelhub import SHConfig, SentinelHubCatalog

# Import from other modules within the same 'core' package
from .credentials_manager import CredentialsManager, Credentials


class SentinelHubAuthenticator:
    """
    Handles the creation and validation of a Sentinel Hub configuration object
    using credentials from a secure manager.
    """

    def __init__(self, credentials_manager: CredentialsManager):
        """
        Initializes the authenticator with a credentials manager.
        """
        self.credentials_manager = credentials_manager

    def authenticate(self, password: str) -> Optional[SHConfig]:
        """
        Loads credentials, creates a SHConfig object, and tests it by making
        a simple API call to verify the credentials are valid.
        """
        print("Authenticator: Attempting to load and decrypt credentials...")
        credentials = self.credentials_manager.load_credentials(password)

        # This is the most likely point of failure. If the password is wrong,
        # `credentials` will be None.
        if not credentials:
            print("❌ Authenticator: Failed to load/decrypt credentials. Is the password correct?")
            return None

        print(f"✅ Authenticator: Credentials decrypted successfully for client_id: ...{credentials.client_id[-4:]}")

        if not self.credentials_manager.validate_credentials(credentials):
            print("❌ Authenticator: Decrypted credentials are not valid (e.g., empty fields).")
            return None

        print("Authenticator: Creating and testing configuration...")
        try:
            # 1. Create the SHConfig object
            config = SHConfig()
            config.sh_client_id = credentials.client_id
            config.sh_client_secret = credentials.client_secret

            # 2. Test the configuration with the CORRECTED method call
            # This will raise an exception if the credentials are bad.
            catalog = SentinelHubCatalog(config=config)
            catalog.get_collections() # CORRECTED METHOD NAME

            print("✅ Authenticator: API test successful. Configuration is valid.")
            return config

        except Exception as e:
            # This will now only catch genuine API or network errors.
            print(f"❌ Authenticator: API test failed. The credentials might be wrong despite successful decryption.")
            print(f"   Error details: {e}")
            return None