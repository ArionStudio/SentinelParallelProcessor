import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import os

from src.gui.widgets.login_form import LoginForm
from src.core.auth.credentials_manager import CredentialsManager, Credentials

class LoginView(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        on_login_success: Callable[[], None],
        padding: int = 20
    ):
        super().__init__(parent, padding=padding)
        self.on_login_success = on_login_success
        self.credentials_manager = CredentialsManager()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create login form
        self.login_form = LoginForm(
            self,
            on_login=self._handle_login
        )
        self.login_form.grid(row=0, column=0, sticky="nsew")
        
        # Check if credentials exist
        self._check_credentials_exist()

    def _check_credentials_exist(self):
        """Check if credentials exist and show appropriate screen"""
        # Check if the encrypted file exists
        if os.path.exists(self.credentials_manager.storage.storage_file):
            # Credentials exist, show password-only screen
            self._show_password_screen()
        else:
            # No credentials, show full credentials screen
            self._show_full_credentials_screen()

    def _show_password_screen(self):
        """Show screen with password field only"""
        self.login_form.clear()
        self.login_form.show_password_only()
        # Add a clear button to reset credentials
        clear_button = ttk.Button(self, text="Clear Credentials", command=self._clear_credentials)
        clear_button.grid(row=1, column=0, pady=10)

    def _show_full_credentials_screen(self):
        """Show screen with all credential fields"""
        self.login_form.clear()
        self.login_form.show_all_fields()

    def _clear_credentials(self):
        """Clear stored credentials and switch to full credentials screen"""
        if self.credentials_manager.clear_credentials():
            messagebox.showinfo("Success", "Credentials cleared.")
            self._show_full_credentials_screen()
        else:
            messagebox.showerror("Error", "Failed to clear credentials.")

    def _handle_login(self, client_id: str, client_secret: str, password: str):
        """Handle login attempt"""
        try:
            # Check if we're in password-only mode
            if not self.login_form.client_id_entry.winfo_viewable():
                # Password-only mode - just try to decrypt existing credentials
                existing_credentials = self.credentials_manager.load_credentials(password)
                if existing_credentials:
                    messagebox.showinfo(
                        "Success",
                        "Login successful!"
                    )
                    self.on_login_success()
                else:
                    messagebox.showerror(
                        "Error",
                        "Invalid password"
                    )
                return

            # Full credentials mode - validate and save new credentials
            credentials = Credentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            if not self.credentials_manager.validate_credentials(credentials):
                messagebox.showerror(
                    "Error",
                    "Please fill in all fields"
                )
                return
            
            # Save new credentials
            if self.credentials_manager.save_credentials(credentials, password):
                messagebox.showinfo(
                    "Success",
                    "New credentials saved and login successful!"
                )
                self.on_login_success()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to save credentials"
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Login failed: {str(e)}"
            ) 