import requests
from typing import Optional, Dict, Any
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Import from other modules within the same 'core' package
from .credentials_manager import CredentialsManager, Credentials


class SentinelHubClient:
    """
    A client to handle OAuth2 authentication and make authenticated requests
    to the Sentinel Hub API.
    """

    TOKEN_URL = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"

    def __init__(self, credentials_manager: CredentialsManager):
        """
        Initializes the client with a credentials manager.

        Args:
            credentials_manager: An instance of CredentialsManager to load
                                 API credentials.
        """
        self.credentials_manager = credentials_manager
        self._session: Optional[OAuth2Session] = None
        self._credentials: Optional[Credentials] = None

    @staticmethod
    def _sentinelhub_compliance_hook(response: requests.Response) -> requests.Response:
        """
        A compliance hook required by Sentinel Hub to handle their
        OAuth2 token response correctly.
        """
        response.raise_for_status()
        return response

    def authenticate(self, password: str) -> bool:
        """
        Authenticates with the Sentinel Hub API using credentials loaded
        from the secure storage.

        Args:
            password: The password to decrypt the stored credentials.

        Returns:
            True if authentication is successful, False otherwise.
        """
        print("Attempting to load credentials...")
        self._credentials = self.credentials_manager.load_credentials(password)

        if not self._credentials or not self.credentials_manager.validate_credentials(
            self._credentials
        ):
            print("Authentication failed: Could not load or validate credentials.")
            return False

        print("Credentials loaded. Attempting to fetch API token...")
        try:
            # 1. Create a backend client with the loaded client_id
            client = BackendApplicationClient(client_id=self._credentials.client_id)

            # 2. Create the OAuth2 session object
            oauth_session = OAuth2Session(client=client)

            # 3. Register the required compliance hook
            oauth_session.register_compliance_hook(
                "access_token_response", self._sentinelhub_compliance_hook
            )

            # 4. Fetch the token
            token = oauth_session.fetch_token(
                token_url=self.TOKEN_URL,
                client_secret=self._credentials.client_secret,
                include_client_id=True,
            )

            if "access_token" in token:
                self._session = oauth_session
                print("Authentication successful. Session is active.")
                return True
            else:
                print("Authentication failed: No access token in response.")
                return False

        except Exception as e:
            print(f"An error occurred during authentication: {e}")
            self._session = None
            return False

    def is_authenticated(self) -> bool:
        """Check if the client session is currently authenticated."""
        return self._session is not None and self._session.authorized

    def get(self, url: str, **kwargs: Any) -> Optional[requests.Response]:
        """
        Makes an authenticated GET request.

        Args:
            url: The URL for the GET request.
            **kwargs: Additional arguments to pass to requests.get().

        Returns:
            A requests.Response object on success, None on failure.
        """
        if not self.is_authenticated():
            print("Error: Client is not authenticated. Please call authenticate() first.")
            return None

        try:
            response = self._session.get(url, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"A network error occurred during GET request: {e}")
            return None

    def post(self, url: str, **kwargs: Any) -> Optional[requests.Response]:
        """
        Makes an authenticated POST request.

        Args:
            url: The URL for the POST request.
            **kwargs: Additional arguments to pass to requests.post() (e.g., json, data).

        Returns:
            A requests.Response object on success, None on failure.
        """
        if not self.is_authenticated():
            print("Error: Client is not authenticated. Please call authenticate() first.")
            return None

        try:
            response = self._session.post(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"A network error occurred during POST request: {e}")
            return None

    def logout(self):
        """Clears the current session."""
        self._session = None
        self._credentials = None
        print("Session has been cleared (logged out).")