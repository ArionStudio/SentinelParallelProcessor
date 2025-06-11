from typing import Optional

# The only imports needed from sentinelhub-py are for configuration and testing.
from sentinelhub import SHConfig, SentinelHubCatalog

# Import from other modules within the same 'core' package
from .credentials_manager import CredentialsManager, Credentials


class SentinelHubAuthenticator:
    """
    Handles the creation and validation of a Sentinel Hub configuration object
    using credentials from a secure manager.

    This class replaces the manual OAuth2 flow. The sentinelhub-py library's
    SHConfig object manages authentication tokens internally for all API calls.
    """

    def __init__(self, credentials_manager: CredentialsManager):
        """
        Initializes the authenticator with a credentials manager.

        Args:
            credentials_manager: An instance of CredentialsManager to load
                                 API credentials.
        """
        self.credentials_manager = credentials_manager

    def authenticate(self, password: str) -> Optional[SHConfig]:
        """
        Loads credentials, creates a SHConfig object, and tests it by making
        a simple API call to verify the credentials are valid.

        Args:
            password: The password to decrypt the stored credentials.

        Returns:
            A validated SHConfig object on success, None on failure.
        """
        print("Authenticator: Attempting to load credentials...")
        credentials = self.credentials_manager.load_credentials(password)

        if not credentials or not self.credentials_manager.validate_credentials(
            credentials
        ):
            print("Authentication failed: Could not load or validate credentials.")
            return None

        print("Authenticator: Credentials loaded. Creating and testing configuration...")
        try:
            # 1. Create the SHConfig object
            config = SHConfig()
            config.sh_client_id = credentials.client_id
            config.sh_client_secret = credentials.client_secret

            # 2. Test the configuration by making a real, low-cost API call.
            # Fetching the list of data collections is a perfect way to verify
            # that the client_id and client_secret are correct.
            # If they are wrong, this line will raise an exception.
            SentinelHubCatalog(config=config).get_collection_list()

            print("Authenticator: Authentication successful. Configuration is valid.")
            # 3. Return the validated config object
            return config

        except Exception as e:
            # This will catch download errors, auth errors (401), etc.
            print(f"Authentication failed during API test: {e}")
            return None