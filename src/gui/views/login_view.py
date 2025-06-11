import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING
import os

from src.gui.widgets.login_form import LoginForm
from src.core.auth.credentials_manager import CredentialsManager, Credentials
from src.core.auth.api_auth import SentinelHubClient  # NEW: Import the client

# To avoid circular imports for type hinting
if TYPE_CHECKING:
    from src.gui.app import MainApplication


class LoginView(ttk.Frame):
    def __init__(self, controller: "MainApplication", **kwargs):
        super().__init__(controller, padding=20, **kwargs)
        self.controller = controller  # CHANGED: Store the controller
        self.credentials_manager = CredentialsManager()

        # Configure grid for centering the form
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create login form
        self.login_form = LoginForm(self, on_login=self._handle_login_attempt)
        self.login_form.grid(row=0, column=0)  # Don't use sticky for centering

        # A frame for the clear button, so it doesn't affect form centering
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, pady=10)

        self._check_credentials_exist()

    def _check_credentials_exist(self):
        """Check if credentials exist and show appropriate screen."""
        if os.path.exists(self.credentials_manager.storage.storage_file):
            self._show_password_screen()
        else:
            self._show_full_credentials_screen()

    def _show_password_screen(self):
        """Show screen with password field only."""
        self.login_form.show_password_only()
        # Add a clear button to reset credentials
        ttk.Button(
            self.button_frame, text="Clear Credentials", command=self._clear_credentials
        ).pack()

    def _show_full_credentials_screen(self):
        """Show screen with all credential fields."""
        self.login_form.show_all_fields()
        # Clear any widgets that might be in the button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def _clear_credentials(self):
        """Clear stored credentials and switch to full credentials screen."""
        if messagebox.askyesno(
            "Confirm", "Are you sure you want to clear stored credentials?"
        ):
            if self.credentials_manager.clear_credentials():
                messagebox.showinfo("Success", "Credentials cleared.")
                self._show_full_credentials_screen()
            else:
                messagebox.showerror("Error", "Failed to clear credentials.")

    def _handle_login_attempt(self, client_id: str, client_secret: str, password: str):
        """
        Handles the login attempt by validating, authenticating with the API,
        and then calling the controller's success callback.
        """
        # Step 1: Validate inputs and save/load credentials locally
        if self.login_form.is_password_only_mode():
            # In password-only mode, we don't need to save, just load.
            # The load happens inside client.authenticate()
            pass
        else:
            # In full mode, first save the credentials
            credentials = Credentials(client_id=client_id, client_secret=client_secret)
            if not self.credentials_manager.validate_credentials(credentials):
                messagebox.showerror("Input Error", "Please fill in all fields.")
                return
            if not self.credentials_manager.save_credentials(credentials, password):
                messagebox.showerror("Storage Error", "Failed to save credentials.")
                return

        # Step 2: Authenticate with the Sentinel Hub API
        try:
            api_client = SentinelHubClient(self.credentials_manager)
            if api_client.authenticate(password):
                messagebox.showinfo("Success", "Authentication successful!")
                # Step 3: Pass the authenticated client back to the controller
                self.controller.on_login_success(api_client)
            else:
                messagebox.showerror(
                    "Authentication Failed",
                    "Could not authenticate with Sentinel Hub. "
                    "Please check your Client ID/Secret and password.",
                )
        except Exception as e:
            messagebox.showerror("Login Error", f"An unexpected error occurred: {e}")