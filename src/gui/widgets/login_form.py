import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class LoginForm(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        on_login: Callable[[str, str, str], None],
        padding: int = 20
    ):
        super().__init__(parent, padding=padding)
        self.on_login = on_login
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Create widgets
        self.client_id_label = ttk.Label(self, text="Client ID:")
        self.client_id_label.grid(row=0, column=0, sticky="w", pady=5)
        self.client_id_entry = ttk.Entry(self)
        self.client_id_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        self.client_secret_label = ttk.Label(self, text="Client Secret:")
        self.client_secret_label.grid(row=1, column=0, sticky="w", pady=5)
        self.client_secret_entry = ttk.Entry(self, show="*")
        self.client_secret_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        self.login_button = ttk.Button(self, text="Login", command=self._handle_login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

    def clear(self):
        """Clear all entry fields"""
        self.client_id_entry.delete(0, tk.END)
        self.client_secret_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_password_only(self):
        """Show only the password field"""
        self.client_id_label.grid_remove()
        self.client_id_entry.grid_remove()
        self.client_secret_label.grid_remove()
        self.client_secret_entry.grid_remove()
        self.password_label.grid()
        self.password_entry.grid()

    def show_all_fields(self):
        """Show all credential fields"""
        self.client_id_label.grid()
        self.client_id_entry.grid()
        self.client_secret_label.grid()
        self.client_secret_entry.grid()
        self.password_label.grid()
        self.password_entry.grid()

    def _handle_login(self):
        """Handle login button click"""
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        password = self.password_entry.get()
        self.on_login(client_id, client_secret, password)

    def set_credentials(self, client_id: str, client_secret: str, password: str):
        """Set the form fields with provided credentials"""
        self.client_id_entry.insert(0, client_id)
        self.client_secret_entry.insert(0, client_secret)
        self.password_entry.insert(0, password) 