import tkinter as tk
from tkinter import ttk
from typing import Callable

class LoginForm(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        on_login: Callable[[str, str, str], None],
        padding: int = 20,
    ):
        super().__init__(parent, padding=padding)
        self.on_login = on_login
        self._password_only_mode = False  # NEW: Add internal state tracking

        self.grid_columnconfigure(1, weight=1)

        # Create widgets (code is unchanged)
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

        self.login_button = ttk.Button(self, text="Login", command=self._trigger_login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

    def clear(self):
        self.client_id_entry.delete(0, tk.END)
        self.client_secret_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_password_only(self):
        self._password_only_mode = True  # NEW
        self.client_id_label.grid_remove()
        self.client_id_entry.grid_remove()
        self.client_secret_label.grid_remove()
        self.client_secret_entry.grid_remove()

    def show_all_fields(self):
        self._password_only_mode = False  # NEW
        self.client_id_label.grid()
        self.client_id_entry.grid()
        self.client_secret_label.grid()
        self.client_secret_entry.grid()

    # NEW: Public method to check the mode
    def is_password_only_mode(self) -> bool:
        return self._password_only_mode

    def _trigger_login(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        password = self.password_entry.get()
        self.on_login(client_id, client_secret, password)